import os
import uuid
import logging
import asyncio
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from supervisor_prompt import supervisor_prompt
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage

# Subagents as tools
from invoice_info_agent.agent import get_invoice_information
from music_catalog_agent.agent import get_music_information

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

ALLOWED_TOOL_NAMES = {
# add hello and fare_well tools
}

# ── Initialize agent ──────────────────────────────────────

async def _build_agent():
    client = MultiServerMCPClient(
        {
            "My-MCP-Server": {
                "transport": "http",
                "url": "http://localhost:8001/mcp",
            }
        }
    )
    all_tools = await client.get_tools()
    supervisor_tools = [t for t in all_tools if t.name in ALLOWED_TOOL_NAMES]

    return create_agent(
        model=llm,
        tools=[get_invoice_information, get_music_information],
        name="supervisor_subagent",
        system_prompt=supervisor_prompt,
    )

_supervisor_agent = asyncio.run(_build_agent())

# ── Debug entrypoint ───────────────────────────────────────────────────────────

async def run_debug():
    query = "My customer ID is 1. How much was my most recent purchase? What albums do you have by U2?"
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    async for chunk in _supervisor_agent.astream(
        {"messages": [HumanMessage(content=query)]},
        config,
        stream_mode="values",
    ):
        chunk["messages"][-1].pretty_print()


if __name__ == "__main__":
    asyncio.run(run_debug())
