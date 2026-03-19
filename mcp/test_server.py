import asyncio

from fastmcp import Client


async def test_server():
    async with Client("http://localhost:8001/mcp") as client:
        # List available tools
        tools = await client.list_tools()
        for tool in tools:
            print(f"--- 🛠️  Tool found: {tool.name} ---")
        # Call say_hello tool
        print("--- 🪛  Calling HELLO tool ---")
        result = await client.call_tool(
            "say_hello"
        )
        print(f"--- ✅  Success: {result.content[0].text} ---")

if __name__ == "__main__":
    asyncio.run(test_server())