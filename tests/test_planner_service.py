import pytest

from multi_agent_system.orchestrator.service import PlannerService


class FakeGraph:
    def __init__(self, result=None, error: Exception | None = None) -> None:
        self.result = result or {}
        self.error = error
        self.calls = []

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


class FakeInterrupt:
    def __init__(self, value) -> None:
        self.value = value


class FakeCapture:
    def __init__(self, error: Exception | None = None) -> None:
        self.calls = []
        self.error = error

    async def capture(self, **kwargs) -> None:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error


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
    service = PlannerService(graph=graph)

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


@pytest.mark.anyio
async def test_planner_service_generates_thread_id_when_missing() -> None:
    graph = FakeGraph(
        result={
            "final_answer": "Done.",
        }
    )
    service = PlannerService(graph=graph)

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
    service = PlannerService(graph=graph)

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
    service = PlannerService(graph=graph)

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
async def test_planner_service_returns_failed_response_when_graph_raises() -> None:
    graph = FakeGraph(error=RuntimeError("graph exploded"))
    service = PlannerService(graph=graph)

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
    service = PlannerService(graph=graph)

    response = await service.invoke(
        "hello",
        thread_id="thread-1",
    )

    assert response.status == "completed"
    assert response.final_answer == "I could not complete the request."


@pytest.mark.anyio
async def test_planner_service_captures_user_visible_interaction() -> None:
    graph = FakeGraph(result={"final_answer": "Latest invoice found."})
    capture = FakeCapture()
    service = PlannerService(graph=graph, capture=capture)

    response = await service.invoke(
        "5",
        thread_id="thread-1",
        resume=True,
    )

    assert capture.calls == [
        {
            "user_input": "5",
            "thread_id": "thread-1",
            "resume": True,
            "response": response,
        }
    ]


@pytest.mark.anyio
async def test_planner_service_capture_failure_does_not_change_response() -> None:
    graph = FakeGraph(result={"final_answer": "Done."})
    capture = FakeCapture(error=RuntimeError("capture unavailable"))
    service = PlannerService(graph=graph, capture=capture)

    response = await service.invoke("hello", thread_id="thread-1")

    assert response.status == "completed"
    assert response.final_answer == "Done."
