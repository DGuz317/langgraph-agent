from pydantic import BaseModel
from typing import List, Any

from langchain.agents import create_agent

from agent_app.common.prompts import AGGREGATOR_AGENT_PROMPT


class ResponseFormat(BaseModel):
    final_answer: str


def build_aggregator_agent(model, checkpointer):
    return create_agent(
        model=model,
        system_prompt=AGGREGATOR_AGENT_PROMPT,
        response_format=ResponseFormat,
        checkpointer=checkpointer,
    )