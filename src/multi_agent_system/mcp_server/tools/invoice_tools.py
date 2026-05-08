import ast

from fastmcp import FastMCP
from langchain_community.utilities import SQLDatabase


def register_invoice_tools(mcp: FastMCP, db: SQLDatabase) -> None:
    @mcp.tool()
    def get_invoices_by_customer_sorted_by_date(customer_id: str) -> list[dict]:
        """
        Look up all invoices for a customer using their ID.
        Results are sorted by invoice date descending.
        """
        result = db.run(
            f"""
            SELECT *
            FROM Invoice
            WHERE CustomerId = {customer_id}
            ORDER BY InvoiceDate DESC;
            """,
            include_columns=True,
        )

        if not result:
            return []

        return ast.literal_eval(result)

    @mcp.tool()
    def get_invoices_sorted_by_unit_price(customer_id: str) -> list[dict]:
        """
        Look up all invoices for a customer and sort invoice lines by unit price descending.
        """
        query = f"""
            SELECT Invoice.*, InvoiceLine.UnitPrice
            FROM Invoice
            JOIN InvoiceLine ON Invoice.InvoiceId = InvoiceLine.InvoiceId
            WHERE Invoice.CustomerId = {customer_id}
            ORDER BY InvoiceLine.UnitPrice DESC;
        """

        result = db.run(query, include_columns=True)

        if not result:
            return []

        return ast.literal_eval(result)

    @mcp.tool()
    def get_employee_by_invoice_and_customer(
        invoice_id: str,
        customer_id: str,
    ) -> dict:
        """
        Return support employee information for a specific invoice and customer.
        """
        query = f"""
            SELECT Employee.FirstName, Employee.Title, Employee.Email
            FROM Employee
            JOIN Customer ON Customer.SupportRepId = Employee.EmployeeId
            JOIN Invoice ON Invoice.CustomerId = Customer.CustomerId
            WHERE Invoice.InvoiceId = {invoice_id}
              AND Invoice.CustomerId = {customer_id};
        """

        result = db.run(query, include_columns=True)

        if not result:
            return {
                "error": (
                    f"No employee found for invoice_id={invoice_id} "
                    f"and customer_id={customer_id}."
                )
            }

        parsed = ast.literal_eval(result)
        return parsed[0] if isinstance(parsed, list) else parsed