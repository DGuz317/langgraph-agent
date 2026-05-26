import os

import httpx
import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_A2A_PAYLOAD_INTEGRATION_TESTS") != "1",
    reason=(
        "Set RUN_A2A_PAYLOAD_INTEGRATION_TESTS=1, configure .env, "
        "and start MCP plus both A2A services to run A2A payload integration tests."
    ),
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_real_planner_api_records_invoice_a2a_payload() -> None:
    from multi_agent_system.orchestrator.server import create_app

    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/planner/invoke",
            json={
                "user_input": "Get latest invoice for customer_id=5",
                "thread_id": "integration-a2a-payload-invoice-thread",
            },
        )

    body = response.json()

    assert response.status_code == 200, body
    assert body["status"] == "completed", body
    assert body["final_answer"]
    assert "failed" not in body["final_answer"].lower()

    task = body["raw_result"]["planner_output"]["tasks"][0]

    assert task["a2a_payload"] == {
        "agent": "invoice",
        "intent": "latest_invoice",
        "args": {"customer_id": "5"},
        "instruction": "Get latest invoice for customer_id=5",
    }


@pytest.mark.anyio
async def test_real_planner_api_records_invoice_detail_payload() -> None:
    from multi_agent_system.orchestrator.server import create_app

    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/planner/invoke",
            json={
                "user_input": "Show invoice detail for invoice_id=361",
                "thread_id": "integration-a2a-payload-invoice-detail-thread",
            },
        )

    body = response.json()

    assert response.status_code == 200, body
    assert body["status"] == "completed", body
    assert body["final_answer"]
    assert "failed" not in body["final_answer"].lower()
    assert "support employee" in body["final_answer"].lower()

    task = body["raw_result"]["planner_output"]["tasks"][0]

    assert task["a2a_payload"] == {
        "agent": "invoice",
        "intent": "invoice_detail",
        "args": {"invoice_id": "361"},
        "instruction": "Get invoice detail for invoice_id=361",
    }


@pytest.mark.anyio
async def test_real_planner_api_records_invoice_summary_payload() -> None:
    from multi_agent_system.orchestrator.server import create_app

    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/planner/invoke",
            json={
                "user_input": "Show total invoice spending for customer_id=5",
                "thread_id": "integration-a2a-payload-invoice-summary-thread",
            },
        )

    body = response.json()

    assert response.status_code == 200, body
    assert body["status"] == "completed", body
    assert body["final_answer"]
    assert "failed" not in body["final_answer"].lower()

    task = body["raw_result"]["planner_output"]["tasks"][0]

    assert task["a2a_payload"] == {
        "agent": "invoice",
        "intent": "invoice_summary",
        "args": {"customer_id": "5"},
        "instruction": "Get invoice summary for customer_id=5",
    }


@pytest.mark.anyio
async def test_real_planner_api_records_music_a2a_payload() -> None:
    from multi_agent_system.orchestrator.server import create_app

    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/planner/invoke",
            json={
                "user_input": "Find tracks by artist AC/DC",
                "thread_id": "integration-a2a-payload-music-thread",
            },
        )

    body = response.json()

    assert response.status_code == 200, body
    assert body["status"] == "completed", body
    assert body["final_answer"]
    assert "failed" not in body["final_answer"].lower()

    task = body["raw_result"]["planner_output"]["tasks"][0]

    assert task["a2a_payload"] == {
        "agent": "music",
        "intent": "tracks_by_artist",
        "args": {"artist": "AC/DC"},
        "instruction": "Find tracks by artist AC/DC",
    }
