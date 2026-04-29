# type:ignore
import asyncio
import json
import os

from contextlib import asynccontextmanager

import click

from dotenv import load_dotenv
from fastmcp.utilities.logging import get_logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult, ReadResourceResult


load_dotenv()
logger = get_logger(__name__)

env = {
    'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
}


@asynccontextmanager
async def init_session(host, port, transport):
    """Initializes and manages an MCP ClientSession based on the specified transport.

    This asynchronous context manager establishes a connection to an MCP server
    using either StreamableHTTP (HTTP) or Standard I/O (STDIO) transport.
    It handles the setup and teardown of the connection and yields an active
    `ClientSession` object ready for communication.

    Args:
        host: The hostname or IP address of the MCP server (used for Streamable-HTTP).
        port: The port number of the MCP server (used for Streamable-HTTP).
        transport: The communication transport to use ('streamable-http' or 'stdio').

    Yields:
        ClientSession: An initialized and ready-to-use MCP client session.

    Raises:
        ValueError: If an unsupported transport type is provided (implicitly,
                    as it won't match 'streamable-http' or 'stdio').
        Exception: Other potential exceptions during client initialization or
                   session setup.
    """
    if transport == 'streamable-http':
        url = f'http://{host}:{port}/mcp'
        async with streamablehttp_client(url) as (read_stream, write_stream, _):
            async with ClientSession(
                read_stream=read_stream, 
                write_stream=write_stream
            ) as session:
                logger.debug('HTTP ClientSession created, initializing...')
                await session.initialize()
                logger.info('HTTP ClientSession initialized successfully.')
                yield session
    elif transport == 'stdio':
        if not os.getenv('GOOGLE_API_KEY'):
            logger.error('GOOGLE_API_KEY is not set')
            raise ValueError('GOOGLE_API_KEY is not set')
        stdio_params = StdioServerParameters(
            command='uv',
            args=['run', 'mcp/server.py'],
            env=env,
        )
        async with stdio_client(stdio_params) as (read_stream, write_stream):
            async with ClientSession(
                read_stream=read_stream,
                write_stream=write_stream,
            ) as session:
                logger.debug('STDIO ClientSession created, initializing...')
                await session.initialize()
                logger.info('STDIO ClientSession initialized successfully.')
                yield session
    else:
        logger.error(f'Unsupported transport type: {transport}')
        raise ValueError(
            f"Unsupported transport type: {transport}. Must be 'streamable-http' or 'stdio'."
        )


async def find_agent(session: ClientSession, query) -> CallToolResult:
    """Calls the 'find_agent' tool on the connected MCP server.

    Args:
        session: The active ClientSession.
        query: The natural language query to send to the 'find_agent' tool.

    Returns:
        The result of the tool call.
    """
    logger.info(f"Calling 'find_agent' tool with query: '{query[:50]}...'")
    return await session.call_tool(
        name='find_agent',
        arguments={
            'query': query,
        },
    )


async def find_resource(session: ClientSession, resource) -> ReadResourceResult:
    """Reads a resource from the connected MCP server.

    Args:
        session: The active ClientSession.
        resource: The URI of the resource to read (e.g., 'resource://agent_cards/list').

    Returns:
        The result of the resource read operation.
    """
    logger.info(f'Reading resource: {resource}')
    return await session.read_resource(resource)


async def get_tracks_by_artist(session: ClientSession, artist: str) -> CallToolResult:
    """Calls the 'get_tracks_by_artist' tool on the connected MCP server.

    Args:
        session: The active ClientSession.
        query: The natural language query to send to the 'get_tracks_by_artist' tool.

    Returns:
        The result of the tool call.
    """
    # TODO: Implementation pending
    logger.info("Calling 'get_tracks_by_artist' tool'")
    return await session.call_tool(
        name='get_tracks_by_artist',
        arguments={
            'artist': artist
        }
    )


async def get_invoices_by_customer_sorted_by_date(session: ClientSession, customer_id: str) -> CallToolResult:
    """Calls the 'get_invoices_by_customer_sorted_by_date' tool on the connected MCP server.

    Args:
        session: The active ClientSession.
        query: The natural language query to send to the 'get_invoices_by_customer_sorted_by_date' tool.

    Returns:
        The result of the tool call.
    """
    # TODO: Implementation pending
    logger.info("Calling 'get_invoices_by_customer_sorted_by_date' tool'")
    return await session.call_tool(
        name='get_invoices_by_customer_sorted_by_date',
        arguments={
            'customer_id': customer_id
        },
    )

# Test util
async def main(host, port, transport, query, resource, tool, tool_input):
    """Main asynchronous function to connect to the MCP server and execute commands.

    Used for local testing.

    Args:
        host: Server hostname.
        port: Server port.
        transport: Connection transport ('streamable-http' or 'stdio').
        query: Optional query string for the 'find_agent' tool.
        resource: Optional resource URI to read.
        tool: Optional tool name to execute. Valid options are:
            'get_invoices_by_customer_sorted_by_date' or 'get_tracks_by_artist'.
    """
    logger.info('Starting Client to connect to MCP')
    async with init_session(host, port, transport) as session:
        if query:
            result = await find_agent(session, query)
            raw = result.content[0].text
            try:
                data = json.loads(raw)
                logger.info(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                logger.info(f'Raw result: {raw}')
        if resource:
            result = await find_resource(session, resource)
            data = json.loads(result.contents[0].text)
            logger.info(json.dumps(data, indent=2))
        if tool:
            if tool == 'get_tracks_by_artist':
                results = await get_tracks_by_artist(session, tool_input)
                logger.info(results.model_dump())
            if tool == 'get_invoices_by_customer_sorted_by_date':
                result = await get_invoices_by_customer_sorted_by_date(session, tool_input)
                raw = result.content[0].text
                try:
                    data = json.loads(raw)
                    logger.info(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    logger.info(f'Raw result: {raw}')

# Command line tester
@click.command()
@click.option('--host', default='localhost', help='Streamable-HTTP Host')
@click.option('--port', default='10000', help='Streamable-HTTP Port')
@click.option('--transport', default='streamable-http', help='MCP Transport')
@click.option('--find_agent', help='Query to find an agent')
@click.option('--resource', help='URI of the resource to locate')
@click.option('--tool_name', type=click.Choice(['get_tracks_by_artist', 'get_invoices_by_customer_sorted_by_date']),
              help='Tool to execute: get_tracks_by_artist or get_invoices_by_customer_sorted_by_date')
@click.option('--tool_input', default=None, help='Input for the tool (artist name or customer_id)')
def cli(host, port, transport, find_agent, resource, tool_name, tool_input):
    """A command-line client to interact with the Agent Cards MCP server."""
    asyncio.run(main(host, port, transport, find_agent, resource, tool_name, tool_input))


if __name__ == '__main__':
    cli()