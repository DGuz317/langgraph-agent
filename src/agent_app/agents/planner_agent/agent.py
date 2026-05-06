from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict, Any

from langchain.agents import create_agent

from agent_app.common.prompts import PLANNER_AGENT_PROMPT


class Task(BaseModel):
    id: int = Field(..., description="Task identifier")
    agent: str = Field(..., description="Target agent name")
    query: str = Field(..., description="Query for the agent")
    description: str = Field(..., description="What the task does")


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

def build_planner_agent(model, checkpointer):
    return create_agent(
        model=model,
        system_prompt=PLANNER_AGENT_PROMPT,
        response_format=ResponseFormat,
        checkpointer=checkpointer,
    )

