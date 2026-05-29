import os
from uuid import uuid4

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


def _create_fast_planner_app():
    from multi_agent_system.orchestrator.server import create_app
    from multi_agent_system.orchestrator.service import PlannerService

    return create_app(
        service=PlannerService(
            capture=None,
            memory_recall=None,
        )
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("user_input", "expected_payload"),
    [
        (
            "Show me 2 most recent invoices of customer id 5",
            {
                "agent": "invoice",
                "intent": "invoice_query",
                "args": {
                    "customer_id": "5",
                    "limit": "2",
                    "sort_by": "invoice_date",
                    "sort_order": "desc",
                    "include_support_employee": "true",
                },
                "instruction": (
                    "Get 2 most recent invoices for customer_id=5 "
                    "with support employee"
                ),
            },
        ),
        (
            "Show total invoice spending for customer_id=5",
            {
                "agent": "invoice",
                "intent": "invoice_summary",
                "args": {"customer_id": "5"},
                "instruction": "Get invoice summary for customer_id=5",
            },
        ),
        (
            "Find tracks by artist AC/DC",
            {
                "agent": "music",
                "intent": "music_query",
                "args": {"search_type": "artist", "artist": "AC/DC"},
                "instruction": "Find tracks by artist AC/DC",
            },
        ),
    ],
)
async def test_real_planner_api_records_structured_a2a_payloads(
    user_input: str,
    expected_payload: dict,
) -> None:
    transport = httpx.ASGITransport(app=_create_fast_planner_app())
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/planner/invoke",
            json={
                "user_input": user_input,
                "thread_id": f"integration-a2a-payload-{uuid4()}",
            },
        )

    body = response.json()

    assert response.status_code == 200, body
    assert body["status"] == "completed", body
    assert body["final_answer"]
    assert "failed" not in body["final_answer"].lower()
    assert body["raw_result"]["planner_output"]["tasks"][0]["a2a_payload"] == (
        expected_payload
    )
