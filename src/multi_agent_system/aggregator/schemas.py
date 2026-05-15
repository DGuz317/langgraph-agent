from pydantic import BaseModel
from typing import Any


class AgentResult(BaseModel):
    agent: str
    result: Any


class AggregatorInput(BaseModel):
    user_input: str
    results: list[AgentResult]


class AggregatorOutput(BaseModel):
    final_answer: str