from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
import os
import asyncio

async def test_tools():
    client = MultiServerMCPClient(
        {
            "My-MCP-Server": {
                "transport": "http",
                "url": "http://localhost:8001/mcp",
            }
        }
    )

    async with client.session("My-MCP-Server") as session:
        tools = await load_mcp_tools(session)

    print(isinstance(tools, list))

if __name__ == "__main__":
    asyncio.run(test_tools())