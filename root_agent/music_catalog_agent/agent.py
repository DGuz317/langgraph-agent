import os
import sys
import ast

from collections.abc import AsyncIterable
from typing import Any, Literal

import httpx

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent
from pydantic import BaseModel
from dotenv import load_dotenv

memory = MemorySaver()
load_dotenv()

sys.path.insert(1, r'C:/Users/nvdung1/Desktop/langraph_agent/database')
import get_database
db = get_database.db 

@tool
def get_albums_by_artist(artist: str):
    """Get albums by an artist."""
    # Execute a SQL query to retrieve album titles and artist names
    # from the Album and Artist tables, joining them and filtering by artist name.
    # `db.run` is a utility from LangChain's SQLDatabase to execute queries.
    # `include_columns=True` ensures column names are included in the result for better readability.
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

@tool
def get_tracks_by_artist(artist: str):
    """Get songs by an artist (or similar artists)."""
    # Execute a SQL query to find tracks (songs) by a given artist, or similar artists.
    # It joins Album, Artist, and Track tables to get song names and artist names.
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

@tool
def get_songs_by_genre(genre: str):
    """
    Fetch songs from the database that match a specific genre.
    
    Args:
        genre (str): The genre of the songs to fetch.
    
    Returns:
        list[dict]: A list of songs that match the specified genre.
    """
    # First, find the GenreId for the given genre name.
    genre_id_query = f"SELECT GenreId FROM Genre WHERE Name LIKE '%{genre}%'"
    genre_ids = db.run(genre_id_query)
    
    # If no genre IDs are found, return an informative message.
    if not genre_ids:
        return f"No songs found for the genre: {genre}"
    
    # Safely evaluate the string result from db.run to get a list of tuples.
    genre_ids = ast.literal_eval(genre_ids)
    # Extract just the GenreId values and join them into a comma-separated string for the IN clause.
    genre_id_list = ", ".join(str(gid[0]) for gid in genre_ids)

    # Construct the query to get songs for the found genre IDs.
    # It joins Track, Album, and Artist tables and limits the results to 8.
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
    
    # If no songs are found for the genre, return an informative message.
    if not songs:
        return f"No songs found for the genre: {genre}"
        
    # Safely evaluate the string result and format it into a list of dictionaries.
    formatted_songs = ast.literal_eval(songs)
    return [
        {"Song": song["SongName"], "Artist": song["ArtistName"]}
        for song in formatted_songs
    ]

@tool
def check_for_songs(song_title: str):
    """Check if a song exists by its name."""
    # Execute a SQL query to check for the existence of a song by its title.
    result = db.run(
        f"""
        SELECT * FROM Track WHERE Name LIKE '%{song_title}%';
        """,
        include_columns=True
    )
    if not result:
        return []
    return ast.literal_eval(result)


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

# client = MultiServerMCPClient(
#     {
#         "My-MCP-Server": {
#             "transport": "http",
#             "url": "http://localhost:8001/mcp",
#         }
#     }
# )

class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str

class MusicAgent:
    """MusicAgent - specifically is to focused on helping customers discover and learn about music in given digital catalog"""

    SYSTEM_INSTRUCTION=(
        """
        You are a member of the assistant team, your role specifically is to focused on helping customers discover and learn about music in our digital catalog. 
        If you are unable to find playlists, songs, or albums associated with an artist, it is okay. 
        Just inform the customer that the catalog does not have any playlists, songs, or albums associated with that artist.
        You also have context on any saved user preferences, helping you to tailor your response. 
        
        CORE RESPONSIBILITIES:
        - Search and provide accurate information about songs, albums, artists, and playlists
        - Offer relevant recommendations based on customer interests
        - Handle music-related queries with attention to detail
        - Help customers discover new music they might enjoy
        - You are routed only when there are questions related to music catalog; ignore other questions. 
        
        SEARCH GUIDELINES:
        1. Always perform thorough searches before concluding something is unavailable
        2. If exact matches aren't found, try:
            - Checking for alternative spellings
            - Looking for similar artist names
            - Searching by partial matches
            - Checking different versions/remixes
        3. When providing song lists:
            - Include the artist name with each song
            - Mention the album when relevant
            - Note if it's part of any playlists
            - Indicate if there are multiple versions
        """
    )

    def __init__(self):
        model_source = os.getenv('model_source', 'google')
        if model_source == 'google':
            self.model = ChatGoogleGenerativeAI(model='gemini-2.5-flash')
        else:
            self.model = ChatOpenAI(
                model=os.getenv('TOOL_LLM_NAME'),
                openai_api_key=os.getenv('API_KEY', 'EMPTY'),
                openai_api_base=os.getenv('TOOL_LLM_URL'),
                temperature=0,
            )

        self.tools = [check_for_songs, 
                        get_songs_by_genre, 
                        get_tracks_by_artist, 
                        get_albums_by_artist]

        self.graph = create_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            system_prompt=self.SYSTEM_INSTRUCTION,
            response_format=ResponseFormat,
        )

    async def stream(self, query, context_id) -> AsyncIterable[dict[str, Any]]:
        inputs = {'messages': [('user', query)]}
        config = {'configurable': {'thread_id': context_id}}

        for item in self.graph.stream(inputs, config, stream_mode='values'):
            message = item['messages'][-1]
            if (
                isinstance(message, AIMessage)
                and message.tool_calls
                and len(message.tool_calls) > 0
            ):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Looking up the database...',
                }
            elif isinstance(message, ToolMessage):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Processing the infomation..',
                }

        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(
            structured_response, ResponseFormat
        ):
            if structured_response.status == 'input_required':
                return {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message,
                }
            if structured_response.status == 'error':
                return {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message,
                }
            if structured_response.status == 'completed':
                return {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.message,
                }

        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': (
                'We are unable to process your request at the moment. '
                'Please try again.'
            ),
        }

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']


# ALLOWED_TOOL_NAMES = {
#     "check_for_songs",
#     "get_songs_by_genre",
#     "get_tracks_by_artist",
#     "get_albums_by_artist",
# }
# music_tools = [t for t in tools if t.name in ALLOWED_TOOL_NAMES]