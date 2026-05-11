from pydantic import BaseModel


class AgentResult(BaseModel):
    agent: str
    result: str


class AggregatorInput(BaseModel):
    user_input: str
    results: list[AgentResult]


class AggregatorOutput(BaseModel):
    final_answer: str