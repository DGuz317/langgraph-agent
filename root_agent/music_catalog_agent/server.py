from python_a2a.langchain import to_a2a_server
from python_a2a import run_server
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
import asyncio, os
from dotenv import load_dotenv
from .music_subagent_prompt import music_subagent_prompt

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

async def build_music_chain():
    client = MultiServerMCPClient({
        "My-MCP-Server": {"transport": "http", "url": "http://localhost:8001/mcp"}
    })
    async with client.session("My-MCP-Server") as session:
        tools = await load_mcp_tools(session)
        ALLOWED = {
            "get_albums_by_artist", 
            "get_tracks_by_artist",
            "get_songs_by_genre", 
            "check_for_songs",
        }
        music_tools = [t for t in tools if t.name in ALLOWED]

        agent = create_agent(
            model=llm,
            tools=music_tools,
            name="music_catalog_agent",
            system_prompt=music_subagent_prompt,
        )
        return agent

if __name__ == "__main__":
    agent = asyncio.run(build_music_chain())

    a2a_server = to_a2a_server(
        agent,
        name="Music Catalog Agent",
        description="Answers questions about songs, albums, artists, and genres.",
    )

    run_server(a2a_server, port=8011)