import json
import os

import httpx
import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INVOICE_SUPPORT_INTEGRATION_TESTS") != "1",
    reason=(
        "Set RUN_INVOICE_SUPPORT_INTEGRATION_TESTS=1, configure .env, "
        "and start MCP plus the invoice A2A service. Start music A2A too for "
        "full planner API parity."
    ),
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _response_data(result: str):
    body = json.loads(result)
    assert body["success"] is True, body
    return body["data"]


def _assert_support_employee(employee: dict) -> None:
    assert employee["FirstName"]
    assert employee["Email"]


@pytest.mark.anyio
async def test_invoice_a2a_all_invoices_include_support_employee() -> None:
    from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient

    result = await InvoiceA2AClient().ask(
        "All my invoice information of customer id 5"
    )

    assert "invoices" in result.lower()
    assert "support employee" in result.lower()
    assert "failed" not in result.lower()
    assert "support_employee" in result
    assert "FirstName" in result
    assert "Email" in result
    data = _response_data(result)
    assert isinstance(data, list) and data
    for entry in data:
        assert "invoice" in entry
        _assert_support_employee(entry["support_employee"])


@pytest.mark.anyio
async def test_invoice_a2a_unit_price_invoices_include_support_employee() -> None:
    from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient

    result = await InvoiceA2AClient().ask(
        "Get invoices sorted by unit price for customer_id=5"
    )

    assert "unit price" in result.lower()
    assert "support employee" in result.lower()
    assert "failed" not in result.lower()
    assert "support_employee" in result
    assert "FirstName" in result
    assert "Email" in result
    data = _response_data(result)
    assert isinstance(data, list) and data
    for entry in data:
        assert "invoice" in entry
        _assert_support_employee(entry["support_employee"])


@pytest.mark.anyio
async def test_invoice_a2a_latest_invoice_includes_support_employee() -> None:
    from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient

    result = await InvoiceA2AClient().ask(
        "Get latest invoice for customer_id=5"
    )

    assert "latest invoice" in result.lower()
    assert "support employee" in result.lower()
    assert "failed" not in result.lower()
    assert "latest_invoice" in result
    assert "support_employee" in result
    assert "FirstName" in result
    assert "Email" in result
    data = _response_data(result)
    assert "latest_invoice" in data
    _assert_support_employee(data["support_employee"])


@pytest.mark.anyio
async def test_invoice_a2a_returns_support_employee_for_latest_invoice() -> None:
    from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient

    result = await InvoiceA2AClient().ask(
        "Get support employee for latest invoice for customer_id=5"
    )

    assert "support employee" in result.lower()
    assert "failed" not in result.lower()
    assert "FirstName" in result
    assert "Email" in result
    data = _response_data(result)
    assert "latest_invoice" in data
    _assert_support_employee(data["support_employee"])


@pytest.mark.anyio
async def test_real_planner_api_returns_support_employee_for_latest_invoice() -> None:
    from multi_agent_system.orchestrator.server import create_app

    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/planner/invoke",
            json={
                "user_input": "Who is the support employee for latest invoice of customer id 5?",
                "thread_id": "integration-invoice-support-employee-thread",
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
    assert task["intent"] == "latest_invoice_support_employee"
    assert task["args"] == {"customer_id": "5"}
    assert task["a2a_payload"] == {
        "agent": "invoice",
        "intent": "latest_invoice_support_employee",
        "args": {"customer_id": "5"},
        "instruction": "Get support employee for latest invoice for customer_id=5",
    }
