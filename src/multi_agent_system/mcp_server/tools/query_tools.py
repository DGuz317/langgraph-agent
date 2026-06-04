import ast
import re

from fastmcp import FastMCP
from langchain_community.utilities import SQLDatabase
from sqlalchemy.exc import SQLAlchemyError


INVOICE_TABLES = {
    "Customer",
    "Employee",
    "Invoice",
    "InvoiceLine",
}
MUSIC_TABLES = {
    "Album",
    "Artist",
    "Genre",
    "MediaType",
    "Playlist",
    "PlaylistTrack",
    "Track",
}


def register_query_tools(mcp: FastMCP, db: SQLDatabase) -> None:
    @mcp.tool()
    def query_invoice_database(sql_query: str) -> list[dict] | dict:
        """
        Run a read-only SELECT query against invoice/customer/support tables.

        Allowed tables: Customer, Employee, Invoice, InvoiceLine.
        Use this when the specific invoice tools do not cover a valid invoice
        database question. The query must be a single SELECT statement.
        """
        return _run_read_only_query(
            db,
            sql_query,
            allowed_tables=INVOICE_TABLES,
        )

    @mcp.tool()
    def query_music_database(sql_query: str) -> list[dict] | dict:
        """
        Run a read-only SELECT query against music catalog tables.

        Allowed tables: Album, Artist, Genre, MediaType, Playlist,
        PlaylistTrack, Track. Use this when the specific music tools do not
        cover a valid music database question. The query must be a single SELECT
        statement.
        """
        return _run_read_only_query(
            db,
            sql_query,
            allowed_tables=MUSIC_TABLES,
        )


def _run_read_only_query(
    db: SQLDatabase,
    sql_query: str,
    *,
    allowed_tables: set[str],
) -> list[dict] | dict:
    cleaned = _validate_select_query(sql_query, allowed_tables=allowed_tables)
    try:
        result = db.run(cleaned, include_columns=True)
    except SQLAlchemyError as exc:
        return {"error": f"Database query failed: {exc}"}

    if not result:
        return []

    parsed = ast.literal_eval(result)
    if isinstance(parsed, list):
        return parsed

    return parsed


def _validate_select_query(
    sql_query: str,
    *,
    allowed_tables: set[str],
) -> str:
    cleaned = sql_query.strip()
    if not cleaned:
        raise ValueError("sql_query must not be empty.")

    if ";" in cleaned.rstrip(";"):
        raise ValueError("Only a single SELECT statement is allowed.")

    cleaned = cleaned.rstrip(";").strip()
    if not re.match(r"(?is)^select\b", cleaned):
        raise ValueError("Only SELECT statements are allowed.")

    forbidden = r"\b(insert|update|delete|drop|alter|create|replace|truncate|attach|detach|pragma|vacuum)\b"
    if re.search(forbidden, cleaned, flags=re.IGNORECASE):
        raise ValueError("Only read-only SELECT statements are allowed.")

    referenced = _referenced_tables(cleaned)
    disallowed = referenced - {table.lower() for table in allowed_tables}
    if disallowed:
        raise ValueError(
            "Query references tables outside this agent domain: "
            + ", ".join(sorted(disallowed))
        )

    if not re.search(r"(?is)\blimit\s+\d+\b", cleaned):
        cleaned = f"{cleaned} LIMIT 20"

    return cleaned


def _referenced_tables(sql_query: str) -> set[str]:
    return {
        match.group(1).split(".")[-1].strip('"`[]').lower()
        for match in re.finditer(
            r"(?is)\b(?:from|join)\s+([A-Za-z_][\w.\"\[\]`]*)",
            sql_query,
        )
    }
