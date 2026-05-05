import os
import asyncio
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict, Any

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from agent_app.common.prompts import PLANNER_AGENT_PROMPT


load_dotenv()
checkpointer = InMemorySaver()


class Task(BaseModel):
    """A single unit of work to be executed by a sub-agent"""
    id: str = Field(..., description="Unique task identifier, e.g. 'task_1', 'task_2'.")
    agent: Literal['invoice_agent', 'music_agent'] = Field(..., description="The agent responsible for executing this task.")
    query: str = Field(
        ..., 
        description=(
            "The self-contained query to send to the agent. "
            "Must include all information the agent needs (e.g. customer ID, artist name) "
            "so it can execute without asking the user for more input."
        )
)


class ResponseFormat(BaseModel):
    """Structured plan produced by the planner agent."""
 
    status: Literal["input_required", "completed", "failed"] = Field(
        ...,
        description=(
            "completed — plan is ready and tasks are populated. "
            "input_required — user must provide more information before planning can proceed. "
            "failed — planner could not interpret the request."
        )
    )
    answer: List[Task] = Field(
        default_factory=list,
        description=(
            "List of tasks to execute. Empty when status is 'input_required' or 'failed'."
        )
    )
    clarification_message: Optional[str] = Field(
        None,
        description=(
            "Populated when status is 'input_required'. "
            "A clear, specific question to relay to the user. "
            "Examples: 'Please provide your customer ID.', 'Which artist are you asking about?'"
        )
    )
    requires_aggregation: bool = Field(
        False,
        description=(
            "True only when the final answer requires combining results from multiple tasks "
            "into a single coherent response. "
            "False when tasks are independent or a single task is sufficient."
        )
    )



MODEL = init_chat_model(
    model=os.getenv("LLM_MODEL"),
    model_provider=os.getenv("MODEL_PROVIDER"),
    base_url=os.getenv("OLLAMA_API_URL"),
    temperature=0,
    timeout=300,
    max_tokens=25000,
)


planner_agent = None 


async def init_planner_agent():
    global planner_agent

    planner_agent = create_agent(
        model=MODEL,
        system_prompt=PLANNER_AGENT_PROMPT,
        response_format=ResponseFormat,
        checkpointer=checkpointer,
    )

    return planner_agent

# --- Simple test ---
# async def _test():
#     await init_planner_agent()
#     result = await planner_agent.ainvoke(
#         {"messages": [{"role": "user", "content": "Show me AC/DC songs and my invoices sorted by price, my customer id is 5"}]},
#         config={"configurable": {"thread_id": "test-1"}},
#     )
#     print(result["structured_response"])
 
 
# if __name__ == "__main__":
#     asyncio.run(_test())

