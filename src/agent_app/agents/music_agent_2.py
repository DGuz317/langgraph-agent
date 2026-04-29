import os
import ast 
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict, Any

from langchain_community.utilities import SQLDatabase
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama

from agent_app.common.prompts import MUSIC_AGENT_PROMPT


load_dotenv()
checkpointer = InMemorySaver()


# --- Databases ---
db = SQLDatabase.from_uri("sqlite:////home/nvdung1/Desktop/MultiAgentSystem/langgraph-agent/src/agent_app/database/chinook.db")

# --- Tools ---
@tool()
def get_albums_by_artist(artist: str):
    """
    Get albums by an artist.
    
    Args:
        artist (str): Name of the artist.

    Returns:
        list[dict]: A list of albums that match the artist name.
    """
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

@tool()
def get_tracks_by_artist(artist: str):
    """
    Get all songs for customer using artist name.
    
    Args:
        artist (str): Name of the artist.

    Returns:
        list[dict]: A list of songs that match the artist name.
    """
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

@tool()
def get_songs_by_genre(genre: str):
    """
    Fetch songs from the database that match a specific genre.
    
    Args:
        genre (str): The genre of the songs to fetch.
    
    Returns:
        list[dict]: A list of songs that match the specified genre.
    """
    genre_id_query = f"SELECT GenreId FROM Genre WHERE Name LIKE '%{genre}%'"
    genre_ids = db.run(genre_id_query)
    if not genre_ids:
        return f"No songs found for the genre: {genre}"
    genre_ids = ast.literal_eval(genre_ids)
    genre_id_list = ", ".join(str(gid[0]) for gid in genre_ids)
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
    if not songs:
        return f"No songs found for the genre: {genre}"
    formatted_songs = ast.literal_eval(songs)
    return [
        {"Song": song["SongName"], "Artist": song["ArtistName"]}
        for song in formatted_songs
    ]

@tool()
def check_for_songs(song_title: str):
    """
    Check if a song exists by its name.
    
    Args:
        song_title (str): Name of the song.

    Returns:
        list[dict]: A list of songs that match the song name.
    """
    result = db.run(
        f"""
        SELECT * FROM Track WHERE Name LIKE '%{song_title}%';
        """,
        include_columns=True
    )
    if not result:
        return []
    return ast.literal_eval(result)

# --- Connect MCP tools ---


class ResponseFormat(BaseModel):
    """Response to user using this format"""
    status: Literal["input_required", "completed", "failed"] = Field(..., description="The current state of the agent's execution loop.")
    task_id: str = Field(..., description="The specific task or query the agent was asked to process.") 
    answer: str = Field(None, description="The generated response or tool output.")
    confidence: float = Field(..., description="Confident score of the answer", ge=0, le=1)


MODEL = init_chat_model(
    model=os.getenv("LLM_MODEL"),
    model_provider="ollama",
    base_url=os.getenv("OLLAMA_API_URL"),
    temperature=0,
    timeout=300,
    max_tokens=25000,
)

invoice_agent = create_agent(
    model=MODEL,
    tools=[
        get_albums_by_artist,
        get_tracks_by_artist,
        get_songs_by_genre,
        check_for_songs
    ],
    system_prompt=MUSIC_AGENT_PROMPT,
    response_format=ResponseFormat,
    checkpointer=checkpointer,
)

# --- Simple test ---
# agent_result = invoice_agent.invoke(
#     {"messages": [{"role": "user", "content": "I like AC/DC. Can you recommend some of their tracks for me?"}]},
#     config={"configurable": {"thread_id": "2"}},
# )

# print(agent_result["messages"][-1].content_blocks)
