from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Literal

from pydantic import BaseModel, Field

EvidenceKind = Literal[
    "planner_decision",
    "hitl_request",
    "hitl_resume",
    "a2a_dispatch",
    "mcp_tool_call",
    "mcp_tool_result",
    "agent_result",
    "aggregation",
]
EvidenceAgent = Literal["planner", "invoice", "music", "aggregator"]
EvidenceStatus = Literal["started", "interrupted", "completed", "failed"]


class ExecutionEvidence(BaseModel):
    """Sanitized workflow evidence eligible for long-lived memory storage."""

    kind: EvidenceKind
    agent: EvidenceAgent
    operation: str
    status: EvidenceStatus
    call_id: str | None = None
    fields: list[str] = Field(default_factory=list)
    arguments: dict[str, Any] = Field(default_factory=dict)
    summary: str


_COLLECTED_EVIDENCE: ContextVar[list[ExecutionEvidence] | None] = ContextVar(
    "collected_execution_evidence",
    default=None,
)


@contextmanager
def collect_execution_evidence() -> Iterator[list[ExecutionEvidence]]:
    """Collect evidence for one request without leaking across concurrent tasks."""
    evidence: list[ExecutionEvidence] = []
    token = _COLLECTED_EVIDENCE.set(evidence)
    try:
        yield evidence
    finally:
        _COLLECTED_EVIDENCE.reset(token)


def record_execution_evidence(evidence: ExecutionEvidence) -> None:
    """Append evidence when a collection scope is active."""
    collected = _COLLECTED_EVIDENCE.get()
    if collected is not None:
        collected.append(evidence)
