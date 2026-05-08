import asyncio
import logging

import click
from fastmcp import FastMCP

from multi_agent_system.config import settings
from multi_agent_system.mcp_server.db import get_db
from multi_agent_system.mcp_server.tools.invoice_tools import register_invoice_tools
from multi_agent_system.mcp_server.tools.music_tools import register_music_tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_mcp_server() -> FastMCP:
    db = get_db()
    mcp = FastMCP("Multi Agent System MCP Server")

    register_invoice_tools(mcp, db)
    register_music_tools(mcp, db)

    return mcp


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10000)
@click.option("--transport", default="streamable-http")
def main(host: str, port: int, transport: str) -> None:
    mcp = create_mcp_server()

    logger.info(
        "Starting MCP server on %s:%s using %s transport",
        host,
        port,
        transport,
    )

    asyncio.run(
        mcp.run_async(
            transport=transport,
            host=host,
            port=port,
        )
    )


if __name__ == "__main__":
    main()