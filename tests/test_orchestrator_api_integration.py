import os

import httpx
import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_ORCHESTRATOR_API_INTEGRATION_TESTS") != "1",
    reason=(
        "Set RUN_ORCHESTRATOR_API_INTEGRATION_TESTS=1, configure .env, "
        "and start MCP plus both A2A services to run planner API integration tests."
    ),
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_real_planner_api_completes_invoice_flow() -> None:
    from multi_agent_system.orchestrator.server import create_app

    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/planner/invoke",
            json={
                "user_input": "Get latest invoice for customer_id=5",
                "thread_id": "integration-invoice-thread",
            },
        )

    body = response.json()

    assert response.status_code == 200, body
    assert body["status"] == "completed", body
    assert body["thread_id"] == "integration-invoice-thread"
    assert body["needs_resume"] is False
    assert body["final_answer"]
    assert "failed" not in body["final_answer"].lower()
    assert "invoice" in body["final_answer"].lower()


@pytest.mark.anyio
async def test_real_planner_api_clarifies_and_continues_same_thread() -> None:
    from multi_agent_system.orchestrator.server import create_app

    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        interrupted = await client.post(
            "/planner/invoke",
            json={
                "user_input": "What is my latest invoice?",
                "thread_id": "integration-hitl-thread",
            },
        )

        interrupted_body = interrupted.json()

        assert interrupted.status_code == 200, interrupted_body
        assert interrupted_body["status"] == "completed", interrupted_body
        assert interrupted_body["thread_id"] == "integration-hitl-thread"
        assert interrupted_body["needs_resume"] is False
        assert interrupted_body["final_answer"]

        completed = await client.post(
            "/planner/invoke",
            json={
                "user_input": "customer id is 5",
                "thread_id": interrupted_body["thread_id"],
            },
        )

    completed_body = completed.json()

    assert completed.status_code == 200, completed_body
    assert completed_body["status"] == "completed", completed_body
    assert completed_body["thread_id"] == "integration-hitl-thread"
    assert completed_body["needs_resume"] is False
    assert completed_body["final_answer"]
    assert "failed" not in completed_body["final_answer"].lower()
    assert "invoice" in completed_body["final_answer"].lower()
