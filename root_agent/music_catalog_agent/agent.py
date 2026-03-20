import os
import uuid
import logging
import asyncio
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from .catalog_subagent_prompt import catalog_subagent_prompt
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

ALLOWED_TOOL_NAMES = {
    "check_for_songs",
    "get_songs_by_genre",
    "get_tracks_by_artist",
    "get_albums_by_artist",
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
    music_tools = [t for t in all_tools if t.name in ALLOWED_TOOL_NAMES]

    return create_agent(
        model=llm,
        tools=music_tools,
        name="music_catalog_information_subagent",
        system_prompt=catalog_subagent_prompt,
    )

_music_agent = asyncio.run(_build_agent())

# Define sub-agent as tool for supervisor-agent
@tool
def get_music_information(request: str) -> str:
    """Get music catalog information using natural language.
    
    Use this when user want to find playlists, songs, or albums associated with an artist.
    Handels search and provide accurate information about songs, albums, artists, and playlists.

    Input: Natural language music catalog information request (e.g., 'I like the Rolling Stones. What songs do you recommend by them or by other artists that I might like?')
    """
    async def _run():
        result = await _music_agent.ainvoke({
            "messages": [HumanMessage(content=request)]
        })
        return result["messages"][-1].content

    return asyncio.run(_run())

# ── Debug entrypoint ───────────────────────────────────────────────────────────

# async def run_debug():
#     query = "I like the Rolling Stones. What songs do you recommend by them or by other artists that I might like?"
#     config = {"configurable": {"thread_id": str(uuid.uuid4())}}

#     async for chunk in _music_agent.astream(
#         {"messages": [HumanMessage(content=query)]},
#         config,
#         stream_mode="values",
#     ):
#         chunk["messages"][-1].pretty_print()


# if __name__ == "__main__":
#     asyncio.run(run_debug())

