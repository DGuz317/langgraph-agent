import pytest

from multi_agent_system.a2a_servers.invoice_agent.agent import InvoiceAgent


@pytest.mark.parametrize(
    ("query", "expected_intent", "expected_customer_id"),
    [
        (
            "Get latest invoice for customer_id=5",
            "latest_invoice",
            "5",
        ),
        (
            "Get invoices sorted by unit price for customer_id=5",
            "invoices_by_unit_price",
            "5",
        ),
        (
            "Get invoices sorted by highest price for customer_id=10",
            "invoices_by_unit_price",
            "10",
        ),
    ],
)
def test_invoice_agent_parse_request(
    query: str,
    expected_intent: str,
    expected_customer_id: str,
) -> None:
    agent = InvoiceAgent()

    request = agent._parse_request(query)

    assert request.intent == expected_intent
    assert request.customer_id == expected_customer_id


def test_invoice_agent_does_not_treat_invoice_id_as_customer_id() -> None:
    agent = InvoiceAgent()

    request = agent._parse_request("Get support employee for invoice_id=77")

    assert request.customer_id is None


def test_invoice_agent_missing_customer_id_fails_validation() -> None:
    agent = InvoiceAgent()

    request = agent._parse_request("Get latest invoice")

    error = agent._validate_request(request)

    assert error is not None
    assert error.success is False
    assert error.content == "Missing required field: customer_id."