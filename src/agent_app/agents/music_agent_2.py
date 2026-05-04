import os
import ast
import asyncio
# import logging
# import colorlog
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict, Any

# from langchain_community.utilities import SQLDatabase
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
# from langchain.tools import tool, ToolRuntime
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
# from langchain_ollama import ChatOllama

from agent_app.common.prompts import MUSIC_AGENT_PROMPT


load_dotenv()
checkpointer = InMemorySaver()
# handler = colorlog.StreamHandler()
# handler.setFormatter(colorlog.ColoredFormatter(
#     "%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s",
#     log_colors={
#         "DEBUG": "cyan",
#         "INFO": "green",
#         "WARNING": "yellow",
#         "ERROR": "red",
#         "CRITICAL": "bold_red",
#     }
# ))

# logger = colorlog.getLogger(__name__)
# logger.addHandler(handler)
# logger.setLevel(logging.INFO)


# --- Defined Response Format ---
class ResponseFormat(BaseModel):
    """Response to user using this format"""
    status: Literal["input_required", "completed", "failed"] = Field(..., description="The current state of the agent's execution loop.")
    task_id: str = Field(..., description="The specific task or query the agent was asked to process.") 
    answer: str = Field(None, description="The generated response or tool output.")
    confidence: float = Field(..., description="Confident score of the answer.", ge=0, le=1)


MODEL = init_chat_model(
    model=os.getenv("LLM_MODEL"),
    model_provider=os.getenv("MODEL_PROVIDER"),
    base_url=os.getenv("OLLAMA_API_URL"),
    temperature=0,
    timeout=300,
    max_tokens=25000,
)

# --- Allowed Tools ---
ALLOWED_TOOL_NAMES = {
    "get_albums_by_artist",
    "get_tracks_by_artist",
    "get_songs_by_genre",
    "check_for_songs",
}

# --- Connect MCP Server ---
async def music_agent_response():
    client = MultiServerMCPClient(
        {
            "data_tools": {
                    "transport": "streamable-http",
                    "url": "http://localhost:10000/mcp"
            }
        }
    )

    async with client.session("data_tools") as session:
        tools = await load_mcp_tools(session)
        music_tools = [t for t in tools if t.name in ALLOWED_TOOL_NAMES]
        # logger.info(f"Allowed tools from MCP Server: {music_tools}")
        music_agent = create_agent(
            model=MODEL,
            tools=music_tools,
            system_prompt=MUSIC_AGENT_PROMPT,
            response_format=ResponseFormat,
            checkpointer=checkpointer,
        )

# --- Simple test ---
        agent_result = await music_agent.ainvoke(
            {"messages": [{"role": "user", "content": "I like AC/DC. Can you recommend some of their tracks for me?"}]},
            config={"configurable": {"thread_id": "2"}},
        )
        # logger.info(f"Agent Response:")
        print(agent_result["messages"][-1].content_blocks)

if __name__ == "__main__":
    asyncio.run(music_agent_response())