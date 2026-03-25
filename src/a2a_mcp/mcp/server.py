import os
import ast
import sys
import json
import asyncio
import requests
import datetime
import openmeteo_requests
from fastmcp import FastMCP
from typing import Optional, Dict, Any, List
import sqlite3
import traceback
from pathlib import Path
from google import genai
import numpy as np
import pandas as pd
import click
import logging
from dotenv import load_dotenv

from a2a_mcp.common.utils import init_api_key
from langchain_community.utilities import SQLDatabase

logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# sys.path.insert(1, r'C:/Users/nvdung1/Desktop/langraph_agent/database')
# import get_database
# db = get_database.db 

# mcp = FastMCP("My-MCP-Server")

AGENT_CARDS_DIR = 'agent_cards'
MODEL = 'gemini-embedding-001'
SQLLITE_DB = 'chinook.db'

def generate_embeddings(text):
    """Generates embeddings for the given text using Google Generative AI.

    Args:
        text: The input string for which to generate embeddings.

    Returns:
        A list of embeddings representing the input text.
    """
    response = client.models.embed_content(
        model=MODEL,
        contents=text,
        config={'task_type': 'RETRIEVAL_DOCUMENT'}
    )
    return response.embeddings[0].values

def load_agent_cards():
    """Loads agent card data from JSON files within a specified directory.

    Returns:
        A list containing JSON data from an agent card file found in the specified directory.
        Returns an empty list if the directory is empty, contains no '.json' files,
        or if all '.json' files encounter errors during processing.
    """
    card_uris = []
    agent_cards = []
    dir_path = Path(AGENT_CARDS_DIR)
    if not dir_path.is_dir():
        logger.error(
            f'Agent cards directory not found or is not a directory: {AGENT_CARDS_DIR}'
        )
        return agent_cards

    logger.info(f'Loading agent cards from card repo: {AGENT_CARDS_DIR}')

    for filename in os.listdir(AGENT_CARDS_DIR):
        if filename.lower().endswith('.json'):
            file_path = dir_path / filename

            if file_path.is_file():
                logger.info(f'Reading file: {filename}')
                try:
                    with file_path.open('r', encoding='utf-8') as f:
                        data = json.load(f)
                        card_uris.append(
                            f'resource://agent_cards/{Path(filename).stem}'
                        )
                        agent_cards.append(data)
                except json.JSONDecodeError as jde:
                    logger.error(f'JSON Decoder Error {jde}')
                except OSError as e:
                    logger.error(f'Error reading file {filename}: {e}.')
                except Exception as e:
                    logger.error(
                        f'An unexpected error occurred processing {filename}: {e}',
                        exc_info=True,
                    )
    logger.info(
        f'Finished loading agent cards. Found {len(agent_cards)} cards.'
    )
    return card_uris, agent_cards

def build_agent_card_embeddings() -> pd.DataFrame:
    """Loads agent cards, generates embeddings for them, and returns a DataFrame.

    Returns:
        Optional[pd.DataFrame]: A Pandas DataFrame containing the original
        'agent_card' data and their corresponding 'Embeddings'. Returns None
        if no agent cards were loaded initially or if an exception occurred
        during the embedding generation process.
    """
    card_uris, agent_cards = load_agent_cards()
    logger.info('Generating Embeddings for agent cards')
    try:
        if agent_cards:
            df = pd.DataFrame(
                {'card_uri': card_uris, 'agent_card': agent_cards}
            )
            df['card_embeddings'] = df.apply(
                lambda row: generate_embeddings(json.dumps(row['agent_card'])),
                axis=1,
            )
            return df
        logger.info('Done generating embeddings for agent cards')
    except Exception as e:
        logger.error(f'An unexpected error occurred : {e}.', exc_info=True)
        return None

def serve(host, port, transport):
    """Initializes and runs the Agent Cards MCP server.

    Args:
        host: The hostname or IP address to bind the server to.
        port: The port number to bind the server to.
        transport: The transport mechanism for the MCP server (e.g., 'stdio', 'sse').

    Raises:
        ValueError: If the 'GOOGLE_API_KEY' environment variable is not set.
    """
    global client
    client = init_api_key()
    logger.info('Starting Agent Cards MCP Server')
    mcp = FastMCP('agent-cards')
    df = build_agent_card_embeddings()
    
    db = SQLDatabase.from_uri(f'sqlite:///{SQLLITE_DB}')

    @mcp.tool(
        name='find_agent',
        description='Finds the most relevant agent card based on a natural language query string.',
    )
    def find_agent(query: str) -> str:
        """Finds the most relevant agent card based on a query string.

        This function takes a user query, typically a natural language question or a task generated by an agent,
        generates its embedding, and compares it against the
        pre-computed embeddings of the loaded agent cards. It uses the dot
        product to measure similarity and identifies the agent card with the
        highest similarity score.

        Args:
            query: The natural language query string used to search for a
                    relevant agent.

        Returns:
            The json representing the agent card deemed most relevant
            to the input query based on embedding similarity.
        """
        query_embedding = client.models.embed_content(
            model=MODEL, 
            contents=query,
        )
        dot_products = np.dot(
            np.stack(df['card_embeddings']), query_embedding.embeddings[0].values
        )
        best_match_index = np.argmax(dot_products)
        logger.debug(
            f'Found best match at index {best_match_index} with score {dot_products[best_match_index]}'
        )
        return json.dumps(df.iloc[best_match_index]['agent_card'])

    @mcp.tool()
    def get_albums_by_artist(artist: str):
        """Get albums by an artist."""
        # Execute a SQL query to retrieve album titles and artist names
        # from the Album and Artist tables, joining them and filtering by artist name.
        # `db.run` is a utility from LangChain's SQLDatabase to execute queries.
        # `include_columns=True` ensures column names are included in the result for better readability.
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
        """Get songs by an artist (or similar artists)."""
        # Execute a SQL query to find tracks (songs) by a given artist, or similar artists.
        # It joins Album, Artist, and Track tables to get song names and artist names.
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
        # First, find the GenreId for the given genre name.
        genre_id_query = f"SELECT GenreId FROM Genre WHERE Name LIKE '%{genre}%'"
        genre_ids = db.run(genre_id_query)
        
        # If no genre IDs are found, return an informative message.
        if not genre_ids:
            return f"No songs found for the genre: {genre}"
        
        # Safely evaluate the string result from db.run to get a list of tuples.
        genre_ids = ast.literal_eval(genre_ids)
        # Extract just the GenreId values and join them into a comma-separated string for the IN clause.
        genre_id_list = ", ".join(str(gid[0]) for gid in genre_ids)

        # Construct the query to get songs for the found genre IDs.
        # It joins Track, Album, and Artist tables and limits the results to 8.
        songs_query = f"""
            SELECT Track.Name as SongName, Artist.Name as ArtistName
            FROM Track
            LEFT JOIN Album ON Track.AlbumId = Album.AlbumId
            LEFT JOIN Artist ON Album.ArtistId = Artist.ArtistId
            WHERE Track.GenreId IN ({genre_id_list})
            GROUP BY Artist.Name
            LIMIT 8;
        """
        songs = db.run(songs_query, include_columns=True)
        
        # If no songs are found for the genre, return an informative message.
        if not songs:
            return f"No songs found for the genre: {genre}"
            
        # Safely evaluate the string result and format it into a list of dictionaries.
        formatted_songs = ast.literal_eval(songs)
        return [
            {"Song": song["SongName"], "Artist": song["ArtistName"]}
            for song in formatted_songs
        ]

    @mcp.tool()
    def check_for_songs(song_title: str):
        """Check if a song exists by its name."""
        # Execute a SQL query to check for the existence of a song by its title.
        result = db.run(
            f"""
            SELECT * FROM Track WHERE Name LIKE '%{song_title}%';
            """,
            include_columns=True
        )
        if not result:
            return []
        return ast.literal_eval(result)

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
        # Executes a SQL query to retrieve all invoice details for a given customer ID,
        # ordered by invoice date in descending order (most recent first).
        result = db.run(
            f"SELECT * FROM Invoice WHERE CustomerId = {customer_id} ORDER BY InvoiceDate DESC;",
            include_columns=True  # ✅ add this so we get dicts
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
        # Executes a SQL query to retrieve invoice details along with the unit price of items in those invoices,
        # for a given customer ID, ordered by unit price in descending order (highest unit price first).
        query = f"""
            SELECT Invoice.*, InvoiceLine.UnitPrice
            FROM Invoice
            JOIN InvoiceLine ON Invoice.InvoiceId = InvoiceLine.InvoiceId
            WHERE Invoice.CustomerId = {customer_id}
            ORDER BY InvoiceLine.UnitPrice DESC;
        """
        result = db.run(query, include_columns=True)  # ✅ add include_columns
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

        # Executes a SQL query to find the employee associated with a specific invoice and customer.
        # It joins Employee, Customer, and Invoice tables to retrieve employee first name, title, and email.
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

    @mcp.resource('resource://agent_cards/list', mime_type='application/json')
    def get_agent_cards() -> dict:
        """Retrieves all loaded agent cards as a json / dictionary for the MCP resource endpoint.

        This function serves as the handler for the MCP resource identified by
        the URI 'resource://agent_cards/list'.

        Returns:
            A json / dictionary structured as {'agent_cards': [...]}, where the value is a
            list containing all the loaded agent card dictionaries. Returns
            {'agent_cards': []} if the data cannot be retrieved.
        """
        # resources = {}
        logger.info('Starting read resources')
        return json.dumps({'agent_cards': df['card_uri'].to_list()})

    @mcp.resource('resource://agent_cards/{card_name}', mime_type='application/json')
    def get_agent_card(card_name: str) -> dict:
        """Retrieves an agent card as a json / dictionary for the MCP resource endpoint.

        This function serves as the handler for the MCP resource identified by
        the URI 'resource://agent_cards/{card_name}'.

        Returns:
            A json / dictionary
        """
        # resources = {}
        logger.info(
            f'Starting read resource resource://agent_cards/{card_name}'
        )
        return json.dumps({
            'agent_card': (
                df.loc[
                    df['card_uri'] == f'resource://agent_cards/{card_name}',
                    'agent_card',
                ]
            ).to_list()
        })

    logger.info(f'Agent cards MCP Server at {host}:{port} and transport {transport}')
    mcp.run(host=host, port=port, transport=transport)

@click.command()
@click.option('--run', 'command', default='mcp-server', help='Command to run')
@click.option('--host', 'host', default='localhost', help='Host for the server')
@click.option('--port', 'port', default=10000, help='Port for the server')
@click.option('--transport', 'transport', default='stdio', help='MCP Transport')
def main(command, host, port, transport) -> None:
    if command == 'mcp-server':
        serve(host, port, transport)
    else:
        raise ValueError(f'Unknown run option: {command}')
 
 
if __name__ == '__main__':
    main()
