import httpx
import pytest

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
        resume: bool | None = None,
    ) -> PlannerServiceResponse:
        self.calls.append(
            {
                "user_input": user_input,
                "thread_id": thread_id,
                "resume": resume,
            }
        )
        return self.response


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def _post(service: FakePlannerService, payload: dict) -> httpx.Response:
    transport = httpx.ASGITransport(app=create_app(service=service))

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.post("/planner/invoke", json=payload)


@pytest.mark.anyio
async def test_planner_api_returns_completed_response() -> None:
    service = FakePlannerService(
        PlannerServiceResponse(
            status="completed",
            thread_id="thread-1",
            final_answer="Done.",
            raw_result={"final_answer": "Done."},
        )
    )
    response = await _post(
        service,
        {
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
            "resume": None,
        }
    ]


@pytest.mark.anyio
async def test_planner_api_returns_interrupted_response() -> None:
    service = FakePlannerService(
        PlannerServiceResponse(
            status="interrupted",
            thread_id="thread-2",
            interrupt_message="Could you provide the song title?",
            needs_resume=True,
        )
    )
    response = await _post(
        service,
        {
            "user_input": "Check for song",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "interrupted"
    assert response.json()["thread_id"] == "thread-2"
    assert response.json()["interrupt_message"] == "Could you provide the song title?"
    assert response.json()["needs_resume"] is True


@pytest.mark.anyio
async def test_planner_api_passes_resume_request_to_service() -> None:
    service = FakePlannerService(
        PlannerServiceResponse(
            status="completed",
            thread_id="thread-2",
            final_answer="Song found.",
        )
    )
    response = await _post(
        service,
        {
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


@pytest.mark.anyio
async def test_planner_api_allows_omitted_resume_for_existing_thread() -> None:
    service = FakePlannerService(
        PlannerServiceResponse(
            status="completed",
            thread_id="thread-2",
            final_answer="Song found.",
        )
    )
    response = await _post(
        service,
        {
            "user_input": "Ligia",
            "thread_id": "thread-2",
        },
    )

    assert response.status_code == 200
    assert service.calls == [
        {
            "user_input": "Ligia",
            "thread_id": "thread-2",
            "resume": None,
        }
    ]


@pytest.mark.anyio
async def test_planner_api_accepts_deprecated_resume_without_thread_id() -> None:
    service = FakePlannerService(
        PlannerServiceResponse(
            status="completed",
            thread_id="unused",
        )
    )
    response = await _post(
        service,
        {
            "user_input": "5",
            "thread_id": None,
            "resume": True,
        },
    )

    assert response.status_code == 200
    assert service.calls == [
        {
            "user_input": "5",
            "thread_id": None,
            "resume": True,
        }
    ]


@pytest.mark.anyio
async def test_planner_api_rejects_blank_user_input() -> None:
    service = FakePlannerService(
        PlannerServiceResponse(
            status="completed",
            thread_id="unused",
        )
    )
    response = await _post(
        service,
        {
            "user_input": "   ",
        },
    )

    assert response.status_code == 422
    assert service.calls == []


@pytest.mark.anyio
async def test_planner_api_trims_user_input() -> None:
    service = FakePlannerService(
        PlannerServiceResponse(
            status="completed",
            thread_id="thread-3",
            final_answer="Done.",
        )
    )
    response = await _post(
        service,
        {
            "user_input": "  Find tracks by artist AC/DC  ",
        },
    )

    assert response.status_code == 200
    assert service.calls[0]["user_input"] == "Find tracks by artist AC/DC"
