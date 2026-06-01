import pytest

from multi_agent_system.planner_app.edges import route_after_invoice, route_after_planner
from multi_agent_system.planner_app.nodes import missing_info_node


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_route_after_planner_routes_by_agent() -> None:
    assert await route_after_planner(
        {"planner_output": {"tasks": [{"agent": "invoice"}]}}
    ) == "invoice"
    assert await route_after_planner(
        {"planner_output": {"tasks": [{"agent": "music"}]}}
    ) == "music"
    assert await route_after_planner(
        {"planner_output": {"tasks": [{"agent": "invoice"}, {"agent": "music"}]}}
    ) == "invoice"


@pytest.mark.anyio
async def test_route_after_planner_routes_missing_info() -> None:
    route = await route_after_planner(
        {
            "missing_fields": ["customer_id"],
            "planner_output": {"tasks": [{"agent": "invoice"}]},
        }
    )

    assert route == "missing_info"


@pytest.mark.anyio
async def test_route_after_invoice_runs_music_when_pending() -> None:
    route = await route_after_invoice(
        {
            "invoice_result": "ok",
            "planner_output": {
                "tasks": [
                    {"agent": "invoice", "status": "completed"},
                    {"agent": "music", "status": "not_started"},
                ]
            },
        }
    )

    assert route == "music"


@pytest.mark.anyio
async def test_missing_info_node_appends_resume_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "multi_agent_system.planner_app.nodes.interrupt_for_missing_info",
        lambda missing_fields: {"genre": "Jazz"},
    )

    result = await missing_info_node(
        {
            "missing_fields": ["genre"],
            "planner_output": {
                "tasks": [
                    {
                        "agent": "music",
                        "instruction": "Recommend 5 songs.",
                        "missing_fields": ["genre"],
                        "status": "not_started",
                    }
                ]
            },
        }
    )

    task = result["planner_output"]["tasks"][0]
    assert "genre=Jazz" in task["instruction"]
    assert result["missing_fields"] == []
