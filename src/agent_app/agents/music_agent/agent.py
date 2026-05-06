import asyncio

from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict, Any

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

from agent_app.common.prompts import MUSIC_AGENT_PROMPT


# --- Defined Response Format ---
class ResponseFormat(BaseModel):
    """Response to user using this format"""
    status: Literal["input_required", "completed", "failed"] = Field(..., description="The current state of the agent's execution loop.")
    task_id: str = Field(..., description="The specific task or query the agent was asked to process.") 
    answer: str = Field(None, description="The generated response or tool output.")
    confidence: float = Field(..., description="Confident score of the answer.", ge=0, le=1)


# --- Allowed Tools ---
ALLOWED_TOOL_NAMES = {
    "get_albums_by_artist",
    "get_tracks_by_artist",
    "get_songs_by_genre",
    "check_for_songs",
}

# --- Build Agent ---
async def build_music_agent(session, model, checkpointer):
    tools = await load_mcp_tools(session)
    music_tools = [t for t in tools if t.name in ALLOWED_TOOL_NAMES]

    return create_agent(
        model=model,
        tools=music_tools,
        system_prompt=MUSIC_AGENT_PROMPT,
        response_format=ResponseFormat,
        checkpointer=checkpointer,
    )
