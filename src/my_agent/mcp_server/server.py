import os
import ast
import click
import asyncio
import logging
import pandas as pd

from fastmcp import FastMCP
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv

from langchain_community.utilities import SQLDatabase

load_dotenv()

logging.basicConfig(level=logging.INFO)

MODEL = os.getenv("EMBED_MODEL")
db = SQLDatabase.from_uri(os.getenv("SQLLITE_DB"))

mcp = FastMCP('MCP Server')

# --- Invoice Tools ---
@mcp.tool()
def get_invoices_by_customer_sorted_by_date(customer_id: str) -> list[dict]:
    """
    Look up all invoices for a customer using their ID.
    The invoices are sorted in descending order by invoice date, which helps when the customer wants to view their most recent/oldest invoice, or if 
    they want to view invoices within a specific date range.
    
    Args:
        customer_id (str): customer_id, which serves as the identifier.
    
    Returns:
        list[dict]: A list of invoices for the customer.
    """
    result = db.run(
        f"SELECT * FROM Invoice WHERE CustomerId = {customer_id} ORDER BY InvoiceDate DESC;",
        include_columns=True
    )
    if not result:
        return []
    return ast.literal_eval(result)

@mcp.tool()
def get_invoices_sorted_by_unit_price(customer_id: str) -> list[dict]:
    """
    Use this tool when the customer wants to know the details of one of their invoices based on the unit price/cost of the invoice.
    This tool looks up all invoices for a customer, and sorts the unit price from highest to lowest. In order to find the invoice associated with the customer, 
    we need to know the customer ID.
    
    Args:
        customer_id (str): customer_id, which serves as the identifier.
    
    Returns:
        list[dict]: A list of invoices sorted by unit price.
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
def get_employee_by_invoice_and_customer(invoice_id: str, customer_id: str) -> dict:
    """
    This tool will take in an invoice ID and a customer ID and return the employee information associated with the invoice.

    Args:
        invoice_id (int): The ID of the specific invoice.
        customer_id (str): customer_id, which serves as the identifier.

    Returns:
        dict: Information about the employee associated with the invoice.
    """
    query = f"""
        SELECT Employee.FirstName, Employee.Title, Employee.Email
        FROM Employee
        JOIN Customer ON Customer.SupportRepId = Employee.EmployeeId
        JOIN Invoice ON Invoice.CustomerId = Customer.CustomerId
        WHERE Invoice.InvoiceId = ({invoice_id}) AND Invoice.CustomerId = ({customer_id});
    """
    result = db.run(query, include_columns=True)
    if not result:
        return {"error": f"No employee found for invoice ID {invoice_id} and customer ID {customer_id}."}
    
    parsed = ast.literal_eval(result)
    return parsed[0] if isinstance(parsed, list) else parsed

# --- Music Tools ---
@mcp.tool()
def get_albums_by_artist(artist: str):
    """
    Get albums by an artist.
    
    Args:
        artist (str): Name of the artist.

    Returns:
        list[dict]: A list of albums that match the artist name.
    """
    result = db.run(
        f"""
        SELECT Album.Title, Artist.Name 
        FROM Album 
        JOIN Artist ON Album.ArtistId = Artist.ArtistId 
        WHERE Artist.Name LIKE '%{artist}%';
        """,
        include_columns=True
    )
    if not result:
        return []
    return ast.literal_eval(result)

@mcp.tool()
def get_tracks_by_artist(artist: str):
    """
    Get all songs for customer using artist name.
    
    Args:
        artist (str): Name of the artist.

    Returns:
        list[dict]: A list of songs that match the artist name.
    """
    result = db.run(
        f"""
        SELECT Track.Name as SongName, Artist.Name as ArtistName 
        FROM Album 
        LEFT JOIN Artist ON Album.ArtistId = Artist.ArtistId 
        LEFT JOIN Track ON Track.AlbumId = Album.AlbumId 
        WHERE Artist.Name LIKE '%{artist}%';
        """,
        include_columns=True
    )
    if not result:
        return []
    return ast.literal_eval(result)

@mcp.tool()
def get_songs_by_genre(genre: str):
    """
    Fetch songs from the database that match a specific genre.
    
    Args:
        genre (str): The genre of the songs to fetch.
    
    Returns:
        list[dict]: A list of songs that match the specified genre.
    """
    genre_id_query = f"SELECT GenreId FROM Genre WHERE Name LIKE '%{genre}%'"
    genre_ids = db.run(genre_id_query)

    if not genre_ids:
        return []

    genre_ids = ast.literal_eval(genre_ids)
    genre_id_list = ", ".join(str(gid[0]) for gid in genre_ids)

    songs_query = f"""
        SELECT Track.Name as SongName, Artist.Name as ArtistName
        FROM Track
        LEFT JOIN Album ON Track.AlbumId = Album.AlbumId
        LEFT JOIN Artist ON Album.ArtistId = Artist.ArtistId
        WHERE Track.GenreId IN ({genre_id_list})
        LIMIT 8;
    """

    songs = db.run(songs_query, include_columns=True)

    if not songs:
        return []
    return ast.literal_eval(songs)

@mcp.tool()
def check_for_songs(song_title: str):
    """
    Check if a song exists by its name.
    
    Args:
        song_title (str): Name of the song.

    Returns:
        list[dict]: A list of songs that match the song name.
    """
    result = db.run(
        f"""
        SELECT * FROM Track WHERE Name LIKE '%{song_title}%';
        """,
        include_columns=True
    )
    if not result:
        return []
    return ast.literal_eval(result)

@click.command()
@click.option('--run', 'command', default='mcp-server')
@click.option('--host','host', default='localhost')
@click.option('--port','port', default=10000)
@click.option('--transport','transport', default='streamable-http')
def main(command, host, port, transport) -> None:
    port = int(os.getenv("PORT", 10000))
    asyncio.run(
        mcp.run_async(
            transport=transport,
            host=host,
            port=port,
        )
    )
if __name__ == '__main__':
    main()