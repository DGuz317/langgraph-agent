import ast
import asyncio
import json
import os
from datetime import datetime
from typing import Any

import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_MCP_INTEGRATION_TESTS") != "1",
    reason="Set RUN_MCP_INTEGRATION_TESTS=1 and configure SQLITE_DB to run MCP integration tests.",
)


@pytest.fixture(scope="module")
def db():
    from multi_agent_system.mcp_server.db import get_db

    return get_db()


@pytest.fixture(scope="module")
def mcp_server(db):
    from fastmcp import FastMCP

    from multi_agent_system.mcp_server.tools.invoice_tools import register_invoice_tools
    from multi_agent_system.mcp_server.tools.music_tools import register_music_tools

    mcp = FastMCP("MCP Tool Integration Tests")
    register_invoice_tools(mcp, db)
    register_music_tools(mcp, db)
    return mcp


def _run_async(coro):
    return asyncio.run(coro)


async def _call_tool_async(mcp_server, tool_name: str, arguments: dict[str, Any]) -> Any:
    from fastmcp import Client

    async with Client(mcp_server) as client:
        result = await client.call_tool(tool_name, arguments)

    return _extract_tool_data(result)


def _call_tool(mcp_server, tool_name: str, arguments: dict[str, Any]) -> Any:
    return _run_async(_call_tool_async(mcp_server, tool_name, arguments))


async def _list_tool_names_async(mcp_server) -> set[str]:
    from fastmcp import Client

    async with Client(mcp_server) as client:
        tools = await client.list_tools()

    return {tool.name for tool in tools}


def _list_tool_names(mcp_server) -> set[str]:
    return _run_async(_list_tool_names_async(mcp_server))


def _extract_tool_data(result: Any) -> Any:
    """
    Normalize FastMCP CallToolResult output into plain Python values.

    FastMCP can expose tool output through:
    - result.data
    - result.structured_content
    - result.content text blocks
    - empty result.content when the tool returns []
    """
    data = getattr(result, "data", None)
    if data is not None:
        return data

    structured_content = getattr(result, "structured_content", None)
    if structured_content is not None:
        if isinstance(structured_content, dict) and "result" in structured_content:
            return structured_content["result"]
        return structured_content

    content = getattr(result, "content", None)

    if content == []:
        return []

    if content:
        text = getattr(content[0], "text", None)
        if text is not None:
            return _parse_text_payload(text)

    return result


def _parse_text_payload(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return text


def _latest_invoice_id_for_customer(db, customer_id: str) -> str:
    result = db.run(
        """
        SELECT InvoiceId
        FROM Invoice
        WHERE CustomerId = :customer_id
        ORDER BY InvoiceDate DESC
        LIMIT 1;
        """,
        parameters={"customer_id": customer_id},
    )

    parsed = ast.literal_eval(result)
    assert parsed, f"Expected at least one invoice for customer_id={customer_id}"
    return str(parsed[0][0])


def _assert_non_empty_list_of_dicts(value: Any) -> list[dict[str, Any]]:
    assert isinstance(value, list)
    assert value, "Expected a non-empty result list."
    assert all(isinstance(row, dict) for row in value)
    return value


def test_all_expected_tools_are_registered(mcp_server) -> None:
    tool_names = _list_tool_names(mcp_server)

    assert {
        "get_invoices_by_customer_sorted_by_date",
        "get_invoices_sorted_by_unit_price",
        "get_employee_by_invoice_and_customer",
        "get_albums_by_artist",
        "get_tracks_by_artist",
        "get_songs_by_genre",
        "check_for_songs",
    }.issubset(tool_names)


# ---------------------------------------------------------------------------
# Invoice tools
# ---------------------------------------------------------------------------


def test_get_invoices_by_customer_sorted_by_date_returns_customer_invoices(mcp_server) -> None:
    customer_id = "5"

    result = _call_tool(
        mcp_server,
        "get_invoices_by_customer_sorted_by_date",
        {"customer_id": customer_id},
    )

    rows = _assert_non_empty_list_of_dicts(result)

    assert all(str(row["CustomerId"]) == customer_id for row in rows)

    invoice_dates = [datetime.fromisoformat(row["InvoiceDate"]) for row in rows]
    assert invoice_dates == sorted(invoice_dates, reverse=True)


def test_get_invoices_by_customer_sorted_by_date_returns_empty_list_for_unknown_customer(mcp_server) -> None:
    result = _call_tool(
        mcp_server,
        "get_invoices_by_customer_sorted_by_date",
        {"customer_id": "999999"},
    )

    assert result == []


def test_get_invoices_sorted_by_unit_price_returns_customer_invoice_lines(mcp_server) -> None:
    customer_id = "5"

    result = _call_tool(
        mcp_server,
        "get_invoices_sorted_by_unit_price",
        {"customer_id": customer_id},
    )

    rows = _assert_non_empty_list_of_dicts(result)

    assert all(str(row["CustomerId"]) == customer_id for row in rows)
    assert all("UnitPrice" in row for row in rows)

    unit_prices = [float(row["UnitPrice"]) for row in rows]
    assert unit_prices == sorted(unit_prices, reverse=True)


def test_get_invoices_sorted_by_unit_price_returns_empty_list_for_unknown_customer(mcp_server) -> None:
    result = _call_tool(
        mcp_server,
        "get_invoices_sorted_by_unit_price",
        {"customer_id": "999999"},
    )

    assert result == []


def test_get_employee_by_invoice_and_customer_returns_support_employee(mcp_server, db) -> None:
    customer_id = "5"
    invoice_id = _latest_invoice_id_for_customer(db, customer_id)

    result = _call_tool(
        mcp_server,
        "get_employee_by_invoice_and_customer",
        {
            "invoice_id": invoice_id,
            "customer_id": customer_id,
        },
    )

    assert isinstance(result, dict)
    assert "error" not in result
    assert result["FirstName"]
    assert result["Title"]
    assert result["Email"]
    assert "@" in result["Email"]


def test_get_employee_by_invoice_and_customer_returns_error_for_invalid_pair(mcp_server) -> None:
    result = _call_tool(
        mcp_server,
        "get_employee_by_invoice_and_customer",
        {
            "invoice_id": "999999",
            "customer_id": "999999",
        },
    )

    assert isinstance(result, dict)
    assert "error" in result
    assert "No employee found" in result["error"]


# ---------------------------------------------------------------------------
# Music tools
# ---------------------------------------------------------------------------


def test_get_albums_by_artist_returns_matching_albums(mcp_server) -> None:
    artist = "AC/DC"

    result = _call_tool(
        mcp_server,
        "get_albums_by_artist",
        {"artist": artist},
    )

    rows = _assert_non_empty_list_of_dicts(result)

    assert all("Title" in row for row in rows)
    assert all("Name" in row for row in rows)
    assert any(artist.lower() in row["Name"].lower() for row in rows)


def test_get_albums_by_artist_returns_empty_list_for_unknown_artist(mcp_server) -> None:
    result = _call_tool(
        mcp_server,
        "get_albums_by_artist",
        {"artist": "Unknown Artist 999999"},
    )

    assert result == []


def test_get_tracks_by_artist_returns_matching_tracks(mcp_server) -> None:
    artist = "AC/DC"

    result = _call_tool(
        mcp_server,
        "get_tracks_by_artist",
        {"artist": artist},
    )

    rows = _assert_non_empty_list_of_dicts(result)

    assert all("SongName" in row for row in rows)
    assert all("ArtistName" in row for row in rows)
    assert all(artist.lower() in row["ArtistName"].lower() for row in rows)


def test_get_tracks_by_artist_returns_empty_list_for_unknown_artist(mcp_server) -> None:
    result = _call_tool(
        mcp_server,
        "get_tracks_by_artist",
        {"artist": "Unknown Artist 999999"},
    )

    assert result == []


def test_get_songs_by_genre_returns_limited_song_recommendations(mcp_server) -> None:
    genre = "Rock"

    result = _call_tool(
        mcp_server,
        "get_songs_by_genre",
        {"genre": genre},
    )

    rows = _assert_non_empty_list_of_dicts(result)

    assert len(rows) <= 8
    assert all("SongName" in row for row in rows)
    assert all("ArtistName" in row for row in rows)


def test_get_songs_by_genre_returns_empty_list_for_unknown_genre(mcp_server) -> None:
    result = _call_tool(
        mcp_server,
        "get_songs_by_genre",
        {"genre": "Unknown Genre 999999"},
    )

    assert result == []


def test_check_for_songs_returns_matching_song(mcp_server) -> None:
    song_title = "For Those About To Rock"

    result = _call_tool(
        mcp_server,
        "check_for_songs",
        {"song_title": song_title},
    )

    rows = _assert_non_empty_list_of_dicts(result)

    assert all("Name" in row for row in rows)
    assert any(song_title.lower() in row["Name"].lower() for row in rows)


def test_check_for_songs_returns_empty_list_for_unknown_song(mcp_server) -> None:
    result = _call_tool(
        mcp_server,
        "check_for_songs",
        {"song_title": "Unknown Song 999999"},
    )

    assert result == []
