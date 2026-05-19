from fastapi.testclient import TestClient

from multi_agent_system.orchestrator.schemas import PlannerServiceResponse
from multi_agent_system.orchestrator.server import create_app


class FakePlannerService:
    def __init__(self, response: PlannerServiceResponse) -> None:
        self.response = response
        self.calls: list[dict] = []

    async def invoke(
        self,
        user_input: str,
        *,
        thread_id: str | None = None,
        resume: bool = False,
    ) -> PlannerServiceResponse:
        self.calls.append(
            {
                "user_input": user_input,
                "thread_id": thread_id,
                "resume": resume,
            }
        )
        return self.response


def test_planner_api_returns_completed_response() -> None:
    service = FakePlannerService(
        PlannerServiceResponse(
            status="completed",
            thread_id="thread-1",
            final_answer="Done.",
            raw_result={"final_answer": "Done."},
        )
    )
    client = TestClient(create_app(service=service))

    response = client.post(
        "/planner/invoke",
        json={
            "user_input": "Get latest invoice for customer_id=5",
            "thread_id": "thread-1",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "completed",
        "thread_id": "thread-1",
        "final_answer": "Done.",
        "interrupt_message": None,
        "needs_resume": False,
        "raw_result": {"final_answer": "Done."},
    }
    assert service.calls == [
        {
            "user_input": "Get latest invoice for customer_id=5",
            "thread_id": "thread-1",
            "resume": False,
        }
    ]


def test_planner_api_returns_interrupted_response() -> None:
    service = FakePlannerService(
        PlannerServiceResponse(
            status="interrupted",
            thread_id="thread-2",
            interrupt_message="Could you provide the song title?",
            needs_resume=True,
        )
    )
    client = TestClient(create_app(service=service))

    response = client.post(
        "/planner/invoke",
        json={
            "user_input": "Check for song",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "interrupted"
    assert response.json()["thread_id"] == "thread-2"
    assert response.json()["interrupt_message"] == "Could you provide the song title?"
    assert response.json()["needs_resume"] is True


def test_planner_api_passes_resume_request_to_service() -> None:
    service = FakePlannerService(
        PlannerServiceResponse(
            status="completed",
            thread_id="thread-2",
            final_answer="Song found.",
        )
    )
    client = TestClient(create_app(service=service))

    response = client.post(
        "/planner/invoke",
        json={
            "user_input": "Ligia",
            "thread_id": "thread-2",
            "resume": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["final_answer"] == "Song found."
    assert service.calls == [
        {
            "user_input": "Ligia",
            "thread_id": "thread-2",
            "resume": True,
        }
    ]


def test_planner_api_rejects_blank_user_input() -> None:
    service = FakePlannerService(
        PlannerServiceResponse(
            status="completed",
            thread_id="unused",
        )
    )
    client = TestClient(create_app(service=service))

    response = client.post(
        "/planner/invoke",
        json={
            "user_input": "   ",
        },
    )

    assert response.status_code == 422
    assert service.calls == []


def test_planner_api_trims_user_input() -> None:
    service = FakePlannerService(
        PlannerServiceResponse(
            status="completed",
            thread_id="thread-3",
            final_answer="Done.",
        )
    )
    client = TestClient(create_app(service=service))

    response = client.post(
        "/planner/invoke",
        json={
            "user_input": "  Find tracks by artist AC/DC  ",
        },
    )

    assert response.status_code == 200
    assert service.calls[0]["user_input"] == "Find tracks by artist AC/DC"
