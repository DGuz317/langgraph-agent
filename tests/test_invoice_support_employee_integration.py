import json
import os
from uuid import uuid4

import httpx
import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INVOICE_SUPPORT_INTEGRATION_TESTS") != "1",
    reason=(
        "Set RUN_INVOICE_SUPPORT_INTEGRATION_TESTS=1, configure .env, "
        "and start MCP plus the invoice A2A service."
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


def _response_data(result: str):
    body = json.loads(result)
    assert body["success"] is True, body
    return body["data"]


def _assert_support_employee(employee: dict) -> None:
    assert employee["FirstName"]
    assert employee["Email"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "payload",
    [
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
        {
            "agent": "invoice",
            "intent": "invoice_query",
            "args": {
                "customer_id": "5",
                "limit": "2",
                "sort_by": "unit_price",
                "sort_order": "desc",
                "include_support_employee": "true",
            },
            "instruction": (
                "Get invoices sorted by unit price desc for customer_id=5 "
                "with support employee"
            ),
        },
    ],
)
async def test_invoice_a2a_invoice_queries_include_support_employee(
    payload: dict,
) -> None:
    from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient

    result = await InvoiceA2AClient().ask_payload(payload)

    assert "support employee" in result.lower()
    assert "failed" not in result.lower()
    data = _response_data(result)
    assert isinstance(data, list) and data
    assert len(data) <= 2
    for entry in data:
        assert "invoice" in entry
        _assert_support_employee(entry["support_employee"])


@pytest.mark.anyio
async def test_invoice_a2a_detail_includes_support_employee() -> None:
    from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient

    result = await InvoiceA2AClient().ask_payload(
        {
            "agent": "invoice",
            "intent": "invoice_query",
            "args": {
                "invoice_id": "361",
                "include_support_employee": "true",
            },
            "instruction": "Get invoice detail for invoice_id=361 with support employee",
        }
    )

    assert "invoice detail" in result.lower()
    assert "support employee" in result.lower()
    data = _response_data(result)
    assert str(data["invoice"]["InvoiceId"]) == "361"
    _assert_support_employee(data["support_employee"])


@pytest.mark.anyio
async def test_invoice_a2a_summary_returns_totals_without_invoice_rows() -> None:
    from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient

    result = await InvoiceA2AClient().ask_payload(
        {
            "agent": "invoice",
            "intent": "invoice_summary",
            "args": {"customer_id": "5"},
            "instruction": "Get invoice summary for customer_id=5",
        }
    )

    data = _response_data(result)
    assert data["CustomerId"] == 5
    assert data["InvoiceCount"] > 0
    assert data["TotalAmount"] > 0
    assert "invoice" not in data
    assert "support_employee" not in data


@pytest.mark.anyio
async def test_invoice_a2a_returns_direct_customer_support_employee_without_invoice_rows() -> None:
    from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient

    result = await InvoiceA2AClient().ask_payload(
        {
            "agent": "invoice",
            "intent": "customer_support_employee",
            "args": {"customer_id": "5"},
            "instruction": "Get support employee for customer_id=5",
        }
    )

    data = _response_data(result)
    assert set(data) == {"support_employee"}
    _assert_support_employee(data["support_employee"])


@pytest.mark.anyio
async def test_real_planner_api_returns_support_employee_for_invoice_query(
) -> None:
    transport = httpx.ASGITransport(app=_create_fast_planner_app())
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/planner/invoke",
            json={
                "user_input": "Who is the support employee for latest invoice of customer id 5?",
                "thread_id": f"integration-invoice-support-{uuid4()}",
            },
        )

    body = response.json()

    assert response.status_code == 200, body
    assert body["status"] == "completed", body
    assert body["final_answer"]
    assert "failed" not in body["final_answer"].lower()
    assert "support employee" in body["final_answer"].lower()

    task = body["raw_result"]["planner_output"]["tasks"][0]
    assert task["agent"] == "invoice"
    assert "customer" in task["instruction"].lower()
    assert "5" in task["instruction"]
    assert "intent" not in task
    assert "args" not in task
    assert "a2a_payload" not in task
