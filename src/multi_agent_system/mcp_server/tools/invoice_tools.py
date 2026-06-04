import ast

from fastmcp import FastMCP
from langchain_community.utilities import SQLDatabase


def register_invoice_tools(mcp: FastMCP, db: SQLDatabase) -> None:
    @mcp.tool()
    def get_invoice_by_id(invoice_id: str) -> dict:
        """
        Look up a single invoice by its ID.
        """
        result = db.run(
            """
            SELECT *
            FROM Invoice
            WHERE InvoiceId = :invoice_id;
            """,
            parameters={"invoice_id": invoice_id},
            include_columns=True,
        )

        if not result:
            return {}

        parsed = ast.literal_eval(result)
        return parsed[0] if isinstance(parsed, list) else parsed

    @mcp.tool()
    def get_invoices_by_customer_sorted_by_date(customer_id: str) -> list[dict]:
        """
        Look up all invoices for a customer using their ID.
        Results are sorted by invoice date descending.
        """
        result = db.run(
            """
            SELECT *
            FROM Invoice
            WHERE CustomerId = :customer_id
            ORDER BY InvoiceDate DESC;
            """,
            parameters={"customer_id": customer_id},
            include_columns=True,
        )

        if not result:
            return []

        return ast.literal_eval(result)

    @mcp.tool()
    def get_invoice_summary_by_customer(customer_id: str) -> dict:
        """
        Return invoice count and total billed amount for a customer.
        """
        result = db.run(
            """
            SELECT CustomerId,
                   COUNT(*) AS InvoiceCount,
                   ROUND(SUM(Total), 2) AS TotalAmount
            FROM Invoice
            WHERE CustomerId = :customer_id
            GROUP BY CustomerId;
            """,
            parameters={"customer_id": customer_id},
            include_columns=True,
        )

        if not result:
            return {}

        parsed = ast.literal_eval(result)
        return parsed[0] if isinstance(parsed, list) else parsed

    @mcp.tool()
    def get_invoices_sorted_by_unit_price(customer_id: str) -> list[dict]:
        """
        Look up all invoices for a customer and sort invoice lines by unit price descending.
        """
        query = """
            SELECT Invoice.*, InvoiceLine.UnitPrice
            FROM Invoice
            JOIN InvoiceLine ON Invoice.InvoiceId = InvoiceLine.InvoiceId
            WHERE Invoice.CustomerId = :customer_id
            ORDER BY InvoiceLine.UnitPrice DESC;
        """

        result = db.run(
            query,
            parameters={"customer_id": customer_id},
            include_columns=True,
        )

        if not result:
            return []

        return ast.literal_eval(result)

    @mcp.tool()
    def get_employee_by_invoice_and_customer(
        invoice_id: str,
        customer_id: str | None = None,
    ) -> dict:
        """
        Return support employee information for a specific invoice.

        If customer_id is provided, it is used as an additional validation
        filter. InvoiceId alone is enough to identify the customer through the
        invoice row.
        """
        query = """
            SELECT Employee.FirstName, Employee.Title, Employee.Email
            FROM Employee
            JOIN Customer ON Customer.SupportRepId = Employee.EmployeeId
            JOIN Invoice ON Invoice.CustomerId = Customer.CustomerId
            WHERE Invoice.InvoiceId = :invoice_id
        """
        parameters = {"invoice_id": invoice_id}
        if customer_id:
            query += " AND Invoice.CustomerId = :customer_id"
            parameters["customer_id"] = customer_id
        query += ";"

        result = db.run(
            query,
            parameters=parameters,
            include_columns=True,
        )

        if not result:
            message = f"No employee found for invoice_id={invoice_id}"
            if customer_id:
                message += f" and customer_id={customer_id}"
            return {"error": f"{message}."}

        parsed = ast.literal_eval(result)
        return parsed[0] if isinstance(parsed, list) else parsed

    @mcp.tool()
    def get_employee_by_customer(customer_id: str) -> dict:
        """
        Return the support employee assigned to a customer.
        """
        result = db.run(
            """
            SELECT Employee.FirstName, Employee.Title, Employee.Email
            FROM Employee
            JOIN Customer ON Customer.SupportRepId = Employee.EmployeeId
            WHERE Customer.CustomerId = :customer_id;
            """,
            parameters={"customer_id": customer_id},
            include_columns=True,
        )

        if not result:
            return {}

        parsed = ast.literal_eval(result)
        return parsed[0] if isinstance(parsed, list) else parsed
