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
    assert graph.calls[0]["config"] == {
        "configurable": {
            "thread_id": "thread-1",
        }
    }
    assert graph.state_calls == [
        {
            "configurable": {
                "thread_id": "thread-1",
            }
        }
    ]


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
async def test_planner_service_returns_interrupt_response() -> None:
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

    assert response.status == "interrupted"
    assert response.thread_id == "thread-1"
    assert response.needs_resume is True
    assert response.interrupt_message == "Could you provide your customer ID?"
    assert response.final_answer is None


@pytest.mark.anyio
async def test_planner_service_resumes_with_command() -> None:
    graph = FakeGraph(
        result={
            "final_answer": "Latest invoice found.",
        }
    )
    service = PlannerService(graph=graph, capture=None, memory_recall=None)

    response = await service.invoke(
        "5",
        thread_id="thread-1",
        resume=True,
    )

    payload = graph.calls[0]["payload"]

    assert response.status == "completed"
    assert response.final_answer == "Latest invoice found."
    assert payload.__class__.__name__ == "Command"
    assert graph.calls[0]["config"]["configurable"]["thread_id"] == "thread-1"


@pytest.mark.anyio
async def test_planner_service_auto_resumes_interrupted_thread() -> None:
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

    payload = graph.calls[0]["payload"]

    assert response.status == "completed"
    assert payload.__class__.__name__ == "Command"


@pytest.mark.anyio
async def test_planner_service_explicit_resume_requires_thread_id() -> None:
    graph = FakeGraph(result={"final_answer": "Done."})
    service = PlannerService(graph=graph, capture=None, memory_recall=None)

    with pytest.raises(ValueError, match="thread_id"):
        await service.invoke("5", resume=True)

    assert graph.calls == []


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
