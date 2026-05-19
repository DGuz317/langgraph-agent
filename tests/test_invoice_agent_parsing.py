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
        (
            "All my invoice information of customer id 5",
            "all_invoices",
            "5",
        ),
        (
            "Get all invoices for customer_id=5",
            "all_invoices",
            "5",
        ),
        (
            "Get support employee for latest invoice for customer_id=5",
            "latest_invoice_support_employee",
            "5",
        ),
        (
            "Who is the support representative for latest invoice of customer id 5?",
            "latest_invoice_support_employee",
            "5",
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


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_invoice_agent_returns_unit_price_invoices_with_support_employee() -> None:
    class StubInvoiceAgent(InvoiceAgent):
        def __init__(self) -> None:
            super().__init__()
            self.calls: list[tuple[str, dict]] = []

        async def call_tool(self, tool_name: str, args: dict):
            self.calls.append((tool_name, args))

            if tool_name == "get_invoices_sorted_by_unit_price":
                return [
                    {
                        "InvoiceId": 77,
                        "CustomerId": 5,
                        "UnitPrice": 1.99,
                    },
                    {
                        "InvoiceId": 78,
                        "CustomerId": 5,
                        "UnitPrice": 0.99,
                    },
                ]

            if tool_name == "get_employee_by_invoice_and_customer":
                return {
                    "FirstName": "Jane",
                    "Title": "Sales Support Agent",
                    "Email": "jane@example.com",
                }

            raise AssertionError(f"Unexpected tool: {tool_name}")

    agent = StubInvoiceAgent()

    response = await agent.ainvoke(
        "Get invoices sorted by unit price for customer_id=5"
    )

    assert response.success is True
    assert response.content == (
        "Found invoices for customer_id=5, sorted by unit price, "
        "with support employee information."
    )
    assert response.data == [
        {
            "invoice": {
                "InvoiceId": 77,
                "CustomerId": 5,
                "UnitPrice": 1.99,
            },
            "support_employee": {
                "FirstName": "Jane",
                "Title": "Sales Support Agent",
                "Email": "jane@example.com",
            },
        },
        {
            "invoice": {
                "InvoiceId": 78,
                "CustomerId": 5,
                "UnitPrice": 0.99,
            },
            "support_employee": {
                "FirstName": "Jane",
                "Title": "Sales Support Agent",
                "Email": "jane@example.com",
            },
        },
    ]
    assert agent.calls == [
        (
            "get_invoices_sorted_by_unit_price",
            {"customer_id": "5"},
        ),
        (
            "get_employee_by_invoice_and_customer",
            {
                "invoice_id": "77",
                "customer_id": "5",
            },
        ),
        (
            "get_employee_by_invoice_and_customer",
            {
                "invoice_id": "78",
                "customer_id": "5",
            },
        ),
    ]


@pytest.mark.anyio
async def test_invoice_agent_returns_all_invoices_with_support_employee() -> None:
    class StubInvoiceAgent(InvoiceAgent):
        def __init__(self) -> None:
            super().__init__()
            self.calls: list[tuple[str, dict]] = []

        async def call_tool(self, tool_name: str, args: dict):
            self.calls.append((tool_name, args))

            if tool_name == "get_invoices_by_customer_sorted_by_date":
                return [
                    {
                        "InvoiceId": 77,
                        "CustomerId": 5,
                    },
                    {
                        "InvoiceId": 78,
                        "CustomerId": 5,
                    },
                ]

            if tool_name == "get_employee_by_invoice_and_customer":
                return {
                    "FirstName": "Jane",
                    "Title": "Sales Support Agent",
                    "Email": "jane@example.com",
                }

            raise AssertionError(f"Unexpected tool: {tool_name}")

    agent = StubInvoiceAgent()

    response = await agent.ainvoke("All my invoice information of customer id 5")

    assert response.success is True
    assert response.content == (
        "Found 2 invoices for customer_id=5 with support employee information."
    )
    assert response.data == [
        {
            "invoice": {
                "InvoiceId": 77,
                "CustomerId": 5,
            },
            "support_employee": {
                "FirstName": "Jane",
                "Title": "Sales Support Agent",
                "Email": "jane@example.com",
            },
        },
        {
            "invoice": {
                "InvoiceId": 78,
                "CustomerId": 5,
            },
            "support_employee": {
                "FirstName": "Jane",
                "Title": "Sales Support Agent",
                "Email": "jane@example.com",
            },
        },
    ]
    assert agent.calls == [
        (
            "get_invoices_by_customer_sorted_by_date",
            {"customer_id": "5"},
        ),
        (
            "get_employee_by_invoice_and_customer",
            {
                "invoice_id": "77",
                "customer_id": "5",
            },
        ),
        (
            "get_employee_by_invoice_and_customer",
            {
                "invoice_id": "78",
                "customer_id": "5",
            },
        ),
    ]


@pytest.mark.anyio
async def test_invoice_agent_returns_latest_invoice_with_support_employee() -> None:
    class StubInvoiceAgent(InvoiceAgent):
        def __init__(self) -> None:
            super().__init__()
            self.calls: list[tuple[str, dict]] = []

        async def call_tool(self, tool_name: str, args: dict):
            self.calls.append((tool_name, args))

            if tool_name == "get_invoices_by_customer_sorted_by_date":
                return [
                    {
                        "InvoiceId": 77,
                        "CustomerId": 5,
                        "InvoiceDate": "2024-01-01 00:00:00",
                    }
                ]

            if tool_name == "get_employee_by_invoice_and_customer":
                return {
                    "FirstName": "Jane",
                    "Title": "Sales Support Agent",
                    "Email": "jane@example.com",
                }

            raise AssertionError(f"Unexpected tool: {tool_name}")

    agent = StubInvoiceAgent()

    response = await agent.ainvoke("Get latest invoice for customer_id=5")

    assert response.success is True
    assert "Latest invoice" in response.content
    assert "Support employee" in response.content
    assert response.data == {
        "latest_invoice": {
            "InvoiceId": 77,
            "CustomerId": 5,
            "InvoiceDate": "2024-01-01 00:00:00",
        },
        "support_employee": {
            "FirstName": "Jane",
            "Title": "Sales Support Agent",
            "Email": "jane@example.com",
        },
    }
    assert agent.calls == [
        (
            "get_invoices_by_customer_sorted_by_date",
            {"customer_id": "5"},
        ),
        (
            "get_employee_by_invoice_and_customer",
            {
                "invoice_id": "77",
                "customer_id": "5",
            },
        ),
    ]


@pytest.mark.anyio
async def test_invoice_agent_returns_support_employee_for_latest_invoice() -> None:
    class StubInvoiceAgent(InvoiceAgent):
        def __init__(self) -> None:
            super().__init__()
            self.calls: list[tuple[str, dict]] = []

        async def call_tool(self, tool_name: str, args: dict):
            self.calls.append((tool_name, args))

            if tool_name == "get_invoices_by_customer_sorted_by_date":
                return [
                    {
                        "InvoiceId": 77,
                        "CustomerId": 5,
                        "InvoiceDate": "2024-01-01 00:00:00",
                    }
                ]

            if tool_name == "get_employee_by_invoice_and_customer":
                return {
                    "FirstName": "Jane",
                    "Title": "Sales Support Agent",
                    "Email": "jane@example.com",
                }

            raise AssertionError(f"Unexpected tool: {tool_name}")

    agent = StubInvoiceAgent()

    response = await agent.ainvoke(
        "Get support employee for latest invoice for customer_id=5"
    )

    assert response.success is True
    assert "Support employee for latest invoice" in response.content
    assert response.data == {
        "latest_invoice": {
            "InvoiceId": 77,
            "CustomerId": 5,
            "InvoiceDate": "2024-01-01 00:00:00",
        },
        "support_employee": {
            "FirstName": "Jane",
            "Title": "Sales Support Agent",
            "Email": "jane@example.com",
        },
    }
    assert agent.calls == [
        (
            "get_invoices_by_customer_sorted_by_date",
            {"customer_id": "5"},
        ),
        (
            "get_employee_by_invoice_and_customer",
            {
                "invoice_id": "77",
                "customer_id": "5",
            },
        ),
    ]


@pytest.mark.anyio
async def test_invoice_agent_returns_no_invoice_for_support_employee_request() -> None:
    class StubInvoiceAgent(InvoiceAgent):
        async def call_tool(self, tool_name: str, args: dict):
            assert tool_name == "get_invoices_by_customer_sorted_by_date"
            assert args == {"customer_id": "999999"}
            return []

    agent = StubInvoiceAgent()

    response = await agent.ainvoke(
        "Get support employee for latest invoice for customer_id=999999"
    )

    assert response.success is True
    assert response.content == "No invoices found for customer_id=999999."
    assert response.data == []
