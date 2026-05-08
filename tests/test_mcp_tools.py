# scripts/test_mcp_tools.py

from multi_agent_system.mcp_server.db import get_db


def main() -> None:
    db = get_db()

    result = db.run(
        "SELECT * FROM Invoice WHERE CustomerId = 5 ORDER BY InvoiceDate DESC LIMIT 1;",
        include_columns=True,
    )

    print(result)


if __name__ == "__main__":
    main()