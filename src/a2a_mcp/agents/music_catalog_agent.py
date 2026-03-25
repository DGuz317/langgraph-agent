import os
import sys
import ast

from collections.abc import AsyncIterable
from typing import Any, Literal, ClassVar

import httpx

from a2a_mcp.common import prompts
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.types import TaskList
from a2a_mcp.common.utils import init_api_key
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent
from pydantic import BaseModel
from dotenv import load_dotenv
import logging

memory = MemorySaver()
logger = logging.getLogger(__name__)

# sys.path.insert(1, r'C:/Users/nvdung1/Desktop/langraph_agent/database')
# import get_database
# db = get_database.db 

# @tool
# def get_albums_by_artist(artist: str):
#     """Get albums by an artist."""
#     # Execute a SQL query to retrieve album titles and artist names
#     # from the Album and Artist tables, joining them and filtering by artist name.
#     # `db.run` is a utility from LangChain's SQLDatabase to execute queries.
#     # `include_columns=True` ensures column names are included in the result for better readability.
#     result = db.run(
#         f"""
#         SELECT Album.Title, Artist.Name 
#         FROM Album 
#         JOIN Artist ON Album.ArtistId = Artist.ArtistId 
#         WHERE Artist.Name LIKE '%{artist}%';
#         """,
#         include_columns=True
#     )
#     if not result:
#         return []
#     return ast.literal_eval(result)

# @tool
# def get_tracks_by_artist(artist: str):
#     """Get songs by an artist (or similar artists)."""
#     # Execute a SQL query to find tracks (songs) by a given artist, or similar artists.
#     # It joins Album, Artist, and Track tables to get song names and artist names.
#     result = db.run(
#         f"""
#         SELECT Track.Name as SongName, Artist.Name as ArtistName 
#         FROM Album 
#         LEFT JOIN Artist ON Album.ArtistId = Artist.ArtistId 
#         LEFT JOIN Track ON Track.AlbumId = Album.AlbumId 
#         WHERE Artist.Name LIKE '%{artist}%';
#         """,
#         include_columns=True
#     )
#     if not result:
#         return []
#     return ast.literal_eval(result)

# @tool
# def get_songs_by_genre(genre: str):
#     """
#     Fetch songs from the database that match a specific genre.
    
#     Args:
#         genre (str): The genre of the songs to fetch.
    
#     Returns:
#         list[dict]: A list of songs that match the specified genre.
#     """
#     # First, find the GenreId for the given genre name.
#     genre_id_query = f"SELECT GenreId FROM Genre WHERE Name LIKE '%{genre}%'"
#     genre_ids = db.run(genre_id_query)
    
#     # If no genre IDs are found, return an informative message.
#     if not genre_ids:
#         return f"No songs found for the genre: {genre}"
    
#     # Safely evaluate the string result from db.run to get a list of tuples.
#     genre_ids = ast.literal_eval(genre_ids)
#     # Extract just the GenreId values and join them into a comma-separated string for the IN clause.
#     genre_id_list = ", ".join(str(gid[0]) for gid in genre_ids)

#     # Construct the query to get songs for the found genre IDs.
#     # It joins Track, Album, and Artist tables and limits the results to 8.
#     songs_query = f"""
#         SELECT Track.Name as SongName, Artist.Name as ArtistName
#         FROM Track
#         LEFT JOIN Album ON Track.AlbumId = Album.AlbumId
#         LEFT JOIN Artist ON Album.ArtistId = Artist.ArtistId
#         WHERE Track.GenreId IN ({genre_id_list})
#         GROUP BY Artist.Name
#         LIMIT 8;
#     """
#     songs = db.run(songs_query, include_columns=True)
    
#     # If no songs are found for the genre, return an informative message.
#     if not songs:
#         return f"No songs found for the genre: {genre}"
        
#     # Safely evaluate the string result and format it into a list of dictionaries.
#     formatted_songs = ast.literal_eval(songs)
#     return [
#         {"Song": song["SongName"], "Artist": song["ArtistName"]}
#         for song in formatted_songs
#     ]

# @tool
# def check_for_songs(song_title: str):
#     """Check if a song exists by its name."""
#     # Execute a SQL query to check for the existence of a song by its title.
#     result = db.run(
#         f"""
#         SELECT * FROM Track WHERE Name LIKE '%{song_title}%';
#         """,
#         include_columns=True
#     )
#     if not result:
#         return []
#     return ast.literal_eval(result)


class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str


class MusicAgent(BaseAgent):
    """MusicAgent - specifically is to focused on helping customers discover and learn about music in given digital catalog"""

    def __init__(self):
        init_api_key()

        logger.info('Initializing MusicAgent')

        super().__init__(
            agent_name='MusicAgent',
            description='Helping customers discover and learn about music in given digital catalog',
            content_types=['text', 'text/plain'],
        )

        self.model = ChatGoogleGenerativeAI(
            model='gemini-2.5-flash'
        )

        self.tools = [check_for_songs, 
                        get_songs_by_genre, 
                        get_tracks_by_artist, 
                        get_albums_by_artist]

        self.graph = create_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            system_prompt=prompts.MUSIC_CATALOG_AGENT,
            response_format=ResponseFormat,
        )

    def invoke(self, query, sessionId) -> str:
        config = {'configurable': {'thread_id': sessionId}}
        self.graph.invoke({'messages': [('user', query)]}, config)
        return self.get_agent_response(config)

    async def stream(self, query, sessionId, task_id) -> AsyncIterable[dict[str, Any]]:
        inputs = {'messages': [('user', query)]}
        config = {'configurable': {'thread_id': sessionId}}

        logger.info(f'Running InvoiceAgent stream for session {sessionId} {task_id} with input {query}')

        for item in self.graph.stream(inputs, config, stream_mode='values'):
            message = item['messages'][-1]
            if isinstance(message, AIMessage):
                yield {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': message.content,
                }
        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(
            structured_response, ResponseFormat
        ):
            if (
                structured_response.status == 'input_required'
                # and structured_response.content.tasks
            ):
                return {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.question,
                }
            if structured_response.status == 'error':
                return {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.question,
                }
            if structured_response.status == 'completed':
                return {
                    'response_type': 'data',
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.content.model_dump(),
                }
        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': 'We are unable to process your request at the moment. Please try again.',
        }



# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     google_api_key=os.getenv("GOOGLE_API_KEY"),
# )

# client = MultiServerMCPClient(
#     {
#         "My-MCP-Server": {
#             "transport": "http",
#             "url": "http://localhost:8001/mcp",
#         }
#     }
# )

# ALLOWED_TOOL_NAMES = {
#     "check_for_songs",
#     "get_songs_by_genre",
#     "get_tracks_by_artist",
#     "get_albums_by_artist",
# }
# music_tools = [t for t in tools if t.name in ALLOWED_TOOL_NAMES]