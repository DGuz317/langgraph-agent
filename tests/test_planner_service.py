import asyncio
from types import SimpleNamespace

import pytest

from multi_agent_system.orchestrator.acontext_memory import MemoryRecallResult
from multi_agent_system.orchestrator.service import PlannerService


class FakeGraph:
    def __init__(
        self,
        result=None,
        error: Exception | None = None,
        *,
        state_interrupts=(),
    ) -> None:
        self.result = result or {}
        self.error = error
        self.state_interrupts = state_interrupts
        self.calls = []
        self.state_calls = []

    async def ainvoke(self, payload, config):
        self.calls.append(
            {
                "payload": payload,
                "config": config,
            }
        )

        if self.error is not None:
            raise self.error

        if callable(self.result):
            return self.result(payload, config)

        return self.result

    async def aget_state(self, config):
        self.state_calls.append(config)
        return SimpleNamespace(interrupts=self.state_interrupts)


class FakeInterrupt:
    def __init__(self, value) -> None:
        self.value = value


class FakeCapture:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.calls = []

    async def capture(self, **kwargs) -> None:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error


class BlockingCapture:
    def __init__(self) -> None:
        self.started = asyncio.Event()
        self.release = asyncio.Event()
        self.calls = []

    async def capture(self, **kwargs) -> None:
        self.calls.append(kwargs)
        self.started.set()
        await self.release.wait()


class FakeMemoryRecall:
    def __init__(
        self,
        result: MemoryRecallResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result or MemoryRecallResult(
            context="- remembered skill",
            metadata={
                "recall_enabled": True,
                "recall_status": "ok",
                "skills_used": 1,
            },
        )
        self.error = error
        self.calls = []

    async def recall(
        self,
        user_input: str,
        *,
        thread_id: str | None = None,
    ) -> MemoryRecallResult:
        self.calls.append(
            {
                "user_input": user_input,
                "thread_id": thread_id,
            }
        )
        if self.error is not None:
            raise self.error
        return self.result


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_planner_service_returns_completed_response() -> None:
    graph = FakeGraph(
        result={
            "final_answer": "Done.",
        }
    )
    service = PlannerService(graph=graph, capture=None, memory_recall=None)

    response = await service.invoke(
        "hello",
        thread_id="thread-1",
    )

    assert response.status == "completed"
    assert response.thread_id == "thread-1"
    assert response.final_answer == "Done."
    assert response.needs_resume is False
    assert graph.calls[0]["payload"] == {"user_input": "hello"}
    assert graph.calls[0]["config"]["configurable"] == {"thread_id": "thread-1"}
    assert graph.calls[0]["config"]["run_name"] == "planner.invoke"
    assert graph.calls[0]["config"]["tags"] == [
        "multi-agent-system",
        "planner",
        "api",
    ]
    assert graph.calls[0]["config"]["metadata"]["thread_id"] == "thread-1"
    assert graph.calls[0]["config"]["metadata"]["request_id"]
    assert graph.state_calls == []


@pytest.mark.anyio
async def test_planner_service_generates_thread_id_when_missing() -> None:
    graph = FakeGraph(
        result={
            "final_answer": "Done.",
        }
    )
    service = PlannerService(graph=graph, capture=None, memory_recall=None)

    response = await service.invoke("hello")

    assert response.status == "completed"
    assert response.thread_id
    assert graph.calls[0]["config"]["configurable"]["thread_id"] == response.thread_id


@pytest.mark.anyio
async def test_planner_service_converts_legacy_interrupt_to_completed_response() -> None:
    graph = FakeGraph(
        result={
            "__interrupt__": [
                FakeInterrupt(
                    {
                        "question": "Could you provide your customer ID?",
                    }
                )
            ]
        }
    )
    service = PlannerService(graph=graph, capture=None, memory_recall=None)

    response = await service.invoke(
        "latest invoice",
        thread_id="thread-1",
    )

    assert response.status == "completed"
    assert response.thread_id == "thread-1"
    assert response.needs_resume is False
    assert response.interrupt_message is None
    assert response.final_answer == "Could you provide your customer ID?"


@pytest.mark.anyio
async def test_planner_service_ignores_deprecated_resume_flag() -> None:
    graph = FakeGraph(
        result={
            "final_answer": "Latest invoice found.",
        },
        state_interrupts=(FakeInterrupt("Provide customer ID."),),
    )
    service = PlannerService(graph=graph, capture=None, memory_recall=None)

    response = await service.invoke(
        "5",
        thread_id="thread-1",
        resume=True,
    )

    assert response.status == "completed"
    assert response.final_answer == "Latest invoice found."
    assert graph.calls[0]["payload"] == {"user_input": "5"}
    assert graph.calls[0]["config"]["configurable"]["thread_id"] == "thread-1"


@pytest.mark.anyio
async def test_planner_service_explicit_resume_without_interrupt_is_follow_up() -> None:
    graph = FakeGraph(
        result={
            "final_answer": "Here are 5 AC/DC tracks.",
        },
        state_interrupts=(),
    )
    service = PlannerService(graph=graph, capture=None, memory_recall=None)

    response = await service.invoke(
        "Show me 5 AC/DC tracks",
        thread_id="thread-1",
        resume=True,
    )

    assert response.status == "completed"
    assert response.final_answer == "Here are 5 AC/DC tracks."
    assert graph.calls[0]["payload"] == {"user_input": "Show me 5 AC/DC tracks"}
    assert graph.calls[0]["config"]["configurable"]["thread_id"] == "thread-1"


@pytest.mark.anyio
async def test_planner_service_same_thread_follow_up_routes_new_request() -> None:
    def result_for_payload(payload, _config):
        if payload == {"user_input": "Show me 5 AC/DC tracks"}:
            return {
                "planner_output": {
                    "tasks": [
                        {
                            "agent": "music",
                            "instruction": "Show 5 AC/DC tracks.",
                            "status": "completed",
                        }
                    ]
                },
                "final_answer": "Music Agent result:\n5 AC/DC tracks",
            }
        return {"final_answer": "stale invoice answer"}

    graph = FakeGraph(result=result_for_payload, state_interrupts=())
    service = PlannerService(graph=graph, capture=None, memory_recall=None)

    response = await service.invoke(
        "Show me 5 AC/DC tracks",
        thread_id="thread-1",
        resume=True,
    )

    assert response.final_answer == "Music Agent result:\n5 AC/DC tracks"
    assert response.raw_result["planner_output"]["tasks"][0]["agent"] == "music"


@pytest.mark.anyio
async def test_planner_service_existing_thread_uses_normal_user_input() -> None:
    graph = FakeGraph(
        result={
            "final_answer": "Latest invoice found.",
        },
        state_interrupts=(FakeInterrupt("Provide customer ID."),),
    )
    service = PlannerService(graph=graph, capture=None, memory_recall=None)

    response = await service.invoke(
        "5",
        thread_id="thread-1",
    )

    assert response.status == "completed"
    assert graph.calls[0]["payload"] == {"user_input": "5"}


@pytest.mark.anyio
async def test_planner_service_deprecated_resume_without_thread_id_is_allowed() -> None:
    graph = FakeGraph(result={"final_answer": "Done."})
    service = PlannerService(graph=graph, capture=None, memory_recall=None)

    response = await service.invoke("5", resume=True)

    assert response.status == "completed"
    assert response.thread_id
    assert graph.calls[0]["payload"] == {"user_input": "5"}


@pytest.mark.anyio
async def test_planner_service_returns_failed_response_when_graph_raises() -> None:
    graph = FakeGraph(error=RuntimeError("graph exploded"))
    service = PlannerService(graph=graph, capture=None, memory_recall=None)

    response = await service.invoke(
        "hello",
        thread_id="thread-1",
    )

    assert response.status == "failed"
    assert response.thread_id == "thread-1"
    assert response.final_answer == "System error: graph exploded"


@pytest.mark.anyio
async def test_planner_service_uses_fallback_answer_when_final_answer_missing() -> None:
    graph = FakeGraph(result={})
    service = PlannerService(graph=graph, capture=None, memory_recall=None)

    response = await service.invoke(
        "hello",
        thread_id="thread-1",
    )

    assert response.status == "completed"
    assert response.final_answer == "I could not complete the request."


@pytest.mark.anyio
async def test_planner_service_captures_user_visible_interaction() -> None:
    graph = FakeGraph(result={"final_answer": "Done."})
    capture = FakeCapture()
    service = PlannerService(graph=graph, capture=capture, memory_recall=None)

    response = await service.invoke("hello", thread_id="thread-capture")

    assert capture.calls == [
        {
            "user_input": "hello",
            "thread_id": "thread-capture",
            "resume": False,
            "response": response,
        }
    ]


@pytest.mark.anyio
async def test_planner_service_capture_failure_does_not_change_response() -> None:
    graph = FakeGraph(result={"final_answer": "Done."})
    capture = FakeCapture(error=RuntimeError("capture offline"))
    service = PlannerService(graph=graph, capture=capture, memory_recall=None)

    response = await service.invoke("hello", thread_id="thread-capture")

    assert response.status == "completed"
    assert response.final_answer == "Done."


@pytest.mark.anyio
async def test_planner_service_can_capture_in_background() -> None:
    graph = FakeGraph(result={"final_answer": "Done."})
    capture = BlockingCapture()
    service = PlannerService(
        graph=graph,
        capture=capture,
        memory_recall=None,
        capture_in_background=True,
    )

    response = await asyncio.wait_for(
        service.invoke("hello", thread_id="thread-background-capture"),
        timeout=1,
    )

    assert response.status == "completed"
    assert response.final_answer == "Done."

    await asyncio.wait_for(capture.started.wait(), timeout=1)
    capture.release.set()
    if service._background_capture_tasks:
        await asyncio.gather(*service._background_capture_tasks)


@pytest.mark.anyio
async def test_planner_service_injects_recalled_memory_context() -> None:
    graph = FakeGraph(
        result={
            "final_answer": "Done.",
            "memory_context": "- remembered skill",
        }
    )
    memory = FakeMemoryRecall()
    service = PlannerService(graph=graph, capture=None, memory_recall=memory)

    response = await service.invoke("latest invoice", thread_id="thread-memory")

    assert memory.calls == [
        {
            "user_input": "latest invoice",
            "thread_id": "thread-memory",
        }
    ]
    assert graph.calls[0]["payload"] == {
        "user_input": "latest invoice",
        "memory_context": "- remembered skill",
    }
    assert response.raw_result["memory"] == {
        "recall_enabled": True,
        "recall_status": "ok",
        "skills_used": 1,
    }
    assert "memory_context" not in response.raw_result


@pytest.mark.anyio
async def test_planner_service_omits_empty_memory_context() -> None:
    graph = FakeGraph(result={"final_answer": "Done."})
    memory = FakeMemoryRecall(
        result=MemoryRecallResult(
            context=None,
            metadata={
                "recall_enabled": True,
                "recall_status": "empty",
                "skills_used": 0,
            },
        )
    )
    service = PlannerService(graph=graph, capture=None, memory_recall=memory)

    response = await service.invoke("hello", thread_id="thread-empty")

    assert graph.calls[0]["payload"] == {"user_input": "hello"}
    assert response.raw_result["memory"]["recall_status"] == "empty"


@pytest.mark.anyio
async def test_planner_service_memory_recall_failure_fails_open() -> None:
    graph = FakeGraph(result={"final_answer": "Done."})
    memory = FakeMemoryRecall(error=RuntimeError("acontext offline"))
    service = PlannerService(graph=graph, capture=None, memory_recall=memory)

    response = await service.invoke("hello", thread_id="thread-failed-memory")

    assert response.status == "completed"
    assert response.final_answer == "Done."
    assert graph.calls[0]["payload"] == {"user_input": "hello"}
    assert response.raw_result["memory"] == {
        "recall_enabled": True,
        "recall_status": "failed",
        "skills_used": 0,
        "skill_names": [],
    }
