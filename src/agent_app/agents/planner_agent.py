import os
import ast 
# import asyncio
# import logging
# import colorlog
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict, Any

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from agent_app.common.prompts import PLANNER_AGENT_PROMT


load_dotenv()
checkpointer = InMemorySaver()


class ResponseFormat(BaseModel):
    """Response to user using this format"""
    status: Literal["input_required", "not_started", "completed", "failed"] = Field(..., description="The current state of the agent's execution loop.")
    answer: List = Field(..., description="List of tasks when the plan is generated.")
    clarification_request: Optional[str] = Field(None, description="Information needed from the user before planning can proceed. The orchestrator should relay this to the user (e.g. customer ID, artist name).")
    requires_aggregation: bool = Field(
        False,
        description=(
            "Set to True only if the final answer requires combining or summarizing results "
            "from multiple tasks or agents into a single coherent response. "
            "Set to False if a single task result is sufficient to directly answer the user's query, "
            "or if multiple tasks are independent and do not need to be merged."
        )
    )
    confidence: float = Field(..., description="Confident score of the answer.", ge=0, le=1)


MODEL = init_chat_model(
    model=os.getenv("LLM_MODEL"),
    model_provider=os.getenv("MODEL_PROVIDER"),
    base_url=os.getenv("OLLAMA_API_URL"),
    temperature=0,
    timeout=300,
    max_tokens=25000,
)

planner_agent = create_agent(
    model=MODEL,
    system_prompt=PLANNER_AGENT_PROMT,
    response_format=ResponseFormat,
    checkpointer=checkpointer,
)

# --- Simple test ---
# agent_result = planner_agent.invoke(
#     {"messages": [{"role": "user", "content": "Show me AC/DC songs and my invoices sorted by price, my customer id is 5"}]},
#     config={"configurable": {"thread_id": "1"}},
# )

# print(agent_result["messages"][-1].content_blocks)
