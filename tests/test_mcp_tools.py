import os

import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_MCP_INTEGRATION_TESTS") != "1",
    reason="Set RUN_MCP_INTEGRATION_TESTS=1 and configure SQLITE_DB to run this test.",
)


def test_mcp_database_can_query_latest_invoice_for_customer() -> None:
    from multi_agent_system.mcp_server.db import get_db

    db = get_db()

    result = db.run(
        "SELECT * FROM Invoice WHERE CustomerId = 5 ORDER BY InvoiceDate DESC LIMIT 1;",
        include_columns=True,
    )

    assert result
    assert "CustomerId" in result
    assert "5" in result
