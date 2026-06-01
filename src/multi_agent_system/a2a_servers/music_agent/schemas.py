from pydantic import BaseModel, Field

from multi_agent_system.common.execution_evidence import ExecutionEvidence


class MusicAgentResponse(BaseModel):
    success: bool
    content: str
    data: list[dict] | dict | None = None
    execution_evidence: list[ExecutionEvidence] = Field(default_factory=list)
