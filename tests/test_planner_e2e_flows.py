import json
from uuid import uuid4

import pytest

from multi_agent_system.planner_app import nodes
from multi_agent_system.planner_app.graph import planner_graph


class FakePlannerOutput:
    def __init__(
        self,
        tasks: list[dict],
        missing_fields: list[str] | None = None,
        requires_aggregation: bool = False,
    ) -> None:
        self.tasks = tasks
        self.missing_fields = missing_fields or []
        self.requires_aggregation = requires_aggregation

    def model_dump(self) -> dict:
        return {
            "status": "completed",
            "tasks": self.tasks,
            "confidence": 1.0,
            "requires_aggregation": self.requires_aggregation,
            "missing_fields": self.missing_fields,
        }


class FakePlanner:
    def __init__(self, output: FakePlannerOutput) -> None:
        self.output = output

    def invoke(self, user_input: str) -> FakePlannerOutput:
        return self.output


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def fake_a2a_clients(monkeypatch: pytest.MonkeyPatch) -> dict[str, list[str]]:
    calls: dict[str, list[str]] = {
        "invoice": [],
        "music": [],
    }

    class FakeInvoiceA2AClient:
        async def ask(self, instruction: str) -> str:
            calls["invoice"].append(instruction)
            return json.dumps(
                {
                    "success": True,
                    "content": "Found latest invoice.",
                    "data": {
                        "InvoiceId": 77,
                        "CustomerId": 5,
                    },
                }
            )

    class FakeMusicA2AClient:
        async def ask(self, instruction: str) -> str:
            calls["music"].append(instruction)
            return json.dumps(
                {
                    "success": True,
                    "content": "Found music result.",
                    "data": [
                        {
                            "SongName": "Desafinado",
                            "ArtistName": "Antônio Carlos Jobim",
                        }
                    ],
                },
                ensure_ascii=False,
            )

    monkeypatch.setattr(nodes, "InvoiceA2AClient", FakeInvoiceA2AClient)
    monkeypatch.setattr(nodes, "MusicA2AClient", FakeMusicA2AClient)

    return calls


def _set_planner_output(
    monkeypatch: pytest.MonkeyPatch,
    tasks: list[dict],
    missing_fields: list[str] | None = None,
    requires_aggregation: bool = False,
) -> None:
    monkeypatch.setattr(
        nodes,
        "planner",
        FakePlanner(
            FakePlannerOutput(
                tasks=tasks,
                missing_fields=missing_fields,
                requires_aggregation=requires_aggregation,
            )
        ),
    )


async def _invoke_graph(user_input: str) -> dict:
    return await planner_graph.ainvoke(
        {"user_input": user_input},
        config={"configurable": {"thread_id": str(uuid4())}},
    )


def _task(
    *,
    agent: str,
    intent: str,
    args: dict[str, str] | None = None,
    missing_fields: list[str] | None = None,
    instruction: str = "stale planner instruction",
) -> dict:
    return {
        "id": str(uuid4()),
        "agent": agent,
        "intent": intent,
        "instruction": instruction,
        "args": args or {},
        "missing_fields": missing_fields or [],
        "status": "not_started",
    }


@pytest.mark.anyio
async def test_planner_e2e_help_query_returns_capabilities(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_planner_output(monkeypatch, tasks=[])

    result = await _invoke_graph("hello, what can you do?")

    assert "invoice" in result["final_answer"].lower()
    assert "music" in result["final_answer"].lower()
    assert "customer_id" in result["final_answer"]


@pytest.mark.anyio
async def test_planner_e2e_direct_invoice_query_uses_args_first_instruction(
    monkeypatch: pytest.MonkeyPatch,
    fake_a2a_clients: dict[str, list[str]],
) -> None:
    _set_planner_output(
        monkeypatch,
        tasks=[
            _task(
                agent="invoice",
                intent="latest_invoice",
                args={"customer_id": "5"},
            )
        ],
    )

    result = await _invoke_graph("Get latest invoice for customer_id=5")

    assert fake_a2a_clients["invoice"] == [
        "Get latest invoice for customer_id=5"
    ]
    assert "Found latest invoice." in result["final_answer"]


@pytest.mark.anyio
async def test_planner_e2e_direct_music_query_uses_args_first_instruction(
    monkeypatch: pytest.MonkeyPatch,
    fake_a2a_clients: dict[str, list[str]],
) -> None:
    _set_planner_output(
        monkeypatch,
        tasks=[
            _task(
                agent="music",
                intent="songs_by_genre",
                args={"genre": "Jazz"},
            )
        ],
    )

    result = await _invoke_graph("Recommend songs by genre Jazz")

    assert fake_a2a_clients["music"] == ["Recommend songs by genre Jazz"]
    assert "Found music result." in result["final_answer"]
    assert "Desafinado" in result["final_answer"]


@pytest.mark.anyio
async def test_planner_e2e_missing_invoice_customer_id_continues_after_hitl(
    monkeypatch: pytest.MonkeyPatch,
    fake_a2a_clients: dict[str, list[str]],
) -> None:
    _set_planner_output(
        monkeypatch,
        tasks=[
            _task(
                agent="invoice",
                intent="latest_invoice",
                missing_fields=["customer_id"],
                instruction="Get latest invoice",
            )
        ],
        missing_fields=["customer_id"],
    )

    def fake_interrupt_for_missing_info(missing_fields: list[str]) -> dict[str, str]:
        assert missing_fields == ["customer_id"]
        return {"customer_id": "5"}

    monkeypatch.setattr(
        nodes,
        "interrupt_for_missing_info",
        fake_interrupt_for_missing_info,
    )

    result = await _invoke_graph("what is my latest invoice?")

    assert fake_a2a_clients["invoice"] == [
        "Get latest invoice for customer_id=5"
    ]
    assert "Found latest invoice." in result["final_answer"]


@pytest.mark.anyio
async def test_planner_e2e_missing_song_title_continues_after_hitl(
    monkeypatch: pytest.MonkeyPatch,
    fake_a2a_clients: dict[str, list[str]],
) -> None:
    _set_planner_output(
        monkeypatch,
        tasks=[
            _task(
                agent="music",
                intent="check_song",
                missing_fields=["song_title"],
                instruction="Check for song",
            )
        ],
        missing_fields=["song_title"],
    )

    def fake_interrupt_for_missing_info(missing_fields: list[str]) -> dict[str, str]:
        assert missing_fields == ["song_title"]
        return {"song_title": "Ligia"}

    monkeypatch.setattr(
        nodes,
        "interrupt_for_missing_info",
        fake_interrupt_for_missing_info,
    )

    result = await _invoke_graph("check for song")

    assert fake_a2a_clients["music"] == ["Check for song Ligia"]
    assert "Found music result." in result["final_answer"]


@pytest.mark.anyio
async def test_planner_e2e_ambiguous_music_defaults_to_genre_after_hitl(
    monkeypatch: pytest.MonkeyPatch,
    fake_a2a_clients: dict[str, list[str]],
) -> None:
    _set_planner_output(
        monkeypatch,
        tasks=[
            _task(
                agent="music",
                intent="clarify_music_search",
                missing_fields=["music_search_type"],
                instruction="Ask whether the user wants music by artist or by genre.",
            )
        ],
        missing_fields=["music_search_type"],
    )

    def fake_interrupt_for_missing_info(missing_fields: list[str]) -> dict[str, str]:
        assert missing_fields == ["music_search_type"]
        return {
            "music_search_type": "genre",
            "genre": "Jazz",
        }

    monkeypatch.setattr(
        nodes,
        "interrupt_for_missing_info",
        fake_interrupt_for_missing_info,
    )

    result = await _invoke_graph("recommend some songs")

    assert fake_a2a_clients["music"] == ["Recommend songs by genre Jazz"]
    assert "Found music result." in result["final_answer"]


@pytest.mark.anyio
async def test_planner_e2e_ambiguous_music_can_choose_artist_after_hitl(
    monkeypatch: pytest.MonkeyPatch,
    fake_a2a_clients: dict[str, list[str]],
) -> None:
    _set_planner_output(
        monkeypatch,
        tasks=[
            _task(
                agent="music",
                intent="clarify_music_search",
                missing_fields=["music_search_type"],
                instruction="Ask whether the user wants music by artist or by genre.",
            )
        ],
        missing_fields=["music_search_type"],
    )

    def fake_interrupt_for_missing_info(missing_fields: list[str]) -> dict[str, str]:
        assert missing_fields == ["music_search_type"]
        return {
            "music_search_type": "artist",
            "artist": "AC/DC",
        }

    monkeypatch.setattr(
        nodes,
        "interrupt_for_missing_info",
        fake_interrupt_for_missing_info,
    )

    result = await _invoke_graph("recommend some songs")

    assert fake_a2a_clients["music"] == ["Find tracks by artist AC/DC"]
    assert "Found music result." in result["final_answer"]


@pytest.mark.anyio
async def test_planner_e2e_multi_agent_query_runs_invoice_then_music(
    monkeypatch: pytest.MonkeyPatch,
    fake_a2a_clients: dict[str, list[str]],
) -> None:
    _set_planner_output(
        monkeypatch,
        tasks=[
            _task(
                agent="invoice",
                intent="latest_invoice",
                args={"customer_id": "5"},
            ),
            _task(
                agent="music",
                intent="tracks_by_artist",
                args={"artist": "AC/DC"},
            ),
        ],
        requires_aggregation=True,
    )

    result = await _invoke_graph(
        "Get latest invoice for customer_id=5 and find tracks by artist AC/DC"
    )

    assert fake_a2a_clients["invoice"] == [
        "Get latest invoice for customer_id=5"
    ]
    assert fake_a2a_clients["music"] == ["Find tracks by artist AC/DC"]
    assert "Found latest invoice." in result["final_answer"]
    assert "Found music result." in result["final_answer"]
