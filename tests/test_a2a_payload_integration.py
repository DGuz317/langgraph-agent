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
    ("user_input", "expected_agent", "expected_text"),
    [
        (
            "Show me 2 most recent invoices of customer id 5",
            "invoice",
            "2",
        ),
        (
            "Show total invoice spending for customer_id=5",
            "invoice",
            "spending",
        ),
        (
            "Find tracks by artist AC/DC",
            "music",
            "AC/DC",
        ),
    ],
)
async def test_real_planner_api_records_agent_instruction_dispatch(
    user_input: str,
    expected_agent: str,
    expected_text: str,
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
                "thread_id": f"integration-agent-dispatch-{uuid4()}",
            },
        )

    body = response.json()

    assert response.status_code == 200, body
    assert body["status"] == "completed", body
    task = body["raw_result"]["planner_output"]["tasks"][0]
    assert task["agent"] == expected_agent
    assert expected_text.lower() in task["instruction"].lower()
    assert "intent" not in task
    assert "args" not in task
