import os
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
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

client = MultiServerMCPClient(
    {
        "My-MCP-Server": {
            "transport": "http",
            "url": "http://localhost:8001/mcp",
        }
    }
)

@tool
async def get_music_agent(request: str) -> str:
    """Get music catalog information using natural language.
    
    Use this when user want to find playlists, songs, or albums associated with an artist.
    Handels search and provide accurate information about songs, albums, artists, and playlists.

    Input: Natural language music catalog information request (e.g., 'I like the Rolling Stones. What songs do you recommend by them or by other artists that I might like?')
    """
    async with client.session("My-MCP-Server") as session:
        tools = await load_mcp_tools(session)

        ALLOWED_TOOL_NAMES = {
            "check_for_songs",
            "get_songs_by_genre",
            "get_tracks_by_artist",
            "get_albums_by_artist",
        }
        music_tools = [t for t in tools if t.name in ALLOWED_TOOL_NAMES]

        agent = create_agent(
            model=llm,
            tools=music_tools,
            name="music_catalog_information_subagent",
            system_prompt=catalog_subagent_prompt,
        )
        final_content = "" 
        
        async for chunk in agent.astream(
            {"messages": [HumanMessage(content=request)]},
            stream_mode="values",
        ):
            if chunk["messages"]:
                last_msg = chunk["messages"][-1]
                last_msg.pretty_print() 
                final_content = last_msg.content

        return final_content