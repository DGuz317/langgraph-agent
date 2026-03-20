import os
import uuid
import logging
import asyncio
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_google_genai import ChatGoogleGenerativeAI
from .catalog_subagent_prompt import catalog_subagent_prompt
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage

logger = logging.getLogger(__name__)
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

client = MultiServerMCPClient(
    {
        "My-MCP-Server": {
            "transport": "http",
            "url": "http://localhost:8001/mcp",
        }
    }
)

# ── Initialize agent ──────────────────────────────────────

async def build_music_agent():
    async with client.session("My-MCP-Server") as session:
        tools = await load_mcp_tools(session)
        music_tools = [t for t in tools if t.name in ALLOWED_TOOL_NAMES]

        agent = create_agent(
            model=llm,
            tools=music_tools,
            name="music_catalog_information_subagent",
            system_prompt=catalog_subagent_prompt,
        )

        logger.info("✅ Music agent ready with persistent MCP session")
        yield agent

# Define sub-agent as tool for supervisor-agent
@tool
async def get_music_information(request: str) -> str:
    """Get music catalog information using natural language.
    
    Use this when user want to find playlists, songs, or albums associated with an artist.
    Handels search and provide accurate information about songs, albums, artists, and playlists.

    Input: Natural language music catalog information request (e.g., 'I like the Rolling Stones. What songs do you recommend by them or by other artists that I might like?')
    """
    async for agent in build_music_agent():
        result = await agent.ainvoke({
            "messages": [HumanMessage(content=request)]
        })
        return result["messages"][-1].content

# ── Debug entrypoint ───────────────────────────────────────────────────────────

# async def run_debug():
#     query = "I like the Rolling Stones. What songs do you recommend by them or by other artists that I might like?"
#     config = {"configurable": {"thread_id": str(uuid.uuid4())}}

#     async for agent in build_music_agent():
#         async for chunk in agent.astream(
#             {"messages": [HumanMessage(content=query)]},
#             config,
#             stream_mode="values",
#         ):
#             chunk["messages"][-1].pretty_print()


# if __name__ == "__main__":
#     asyncio.run(run_debug())

