import pytest

from multi_agent_system.a2a_servers.invoice_agent.agent import InvoiceAgent
from multi_agent_system.common.agent_runtime import AgentRunResult


class RecordingRuntime:
    def __init__(self, result: AgentRunResult | None = None) -> None:
        self.instructions: list[str] = []
        self.result = result or AgentRunResult(
            success=True,
            content="Invoice answer.",
        )

    async def ainvoke(self, instruction: str) -> AgentRunResult:
        self.instructions.append(instruction)
        return self.result


@pytest.mark.anyio
async def test_invoice_agent_delegates_instruction_to_runtime() -> None:
    runtime = RecordingRuntime()
    agent = InvoiceAgent(runtime=runtime)

    response = await agent.ainvoke(
        "Show 3 most recent invoices for customer id=7."
    )

    assert response.success is True
    assert response.content == "Invoice answer."
    assert runtime.instructions == [
        "Show 3 most recent invoices for customer id=7."
    ]


@pytest.mark.anyio
async def test_invoice_agent_returns_runtime_failure() -> None:
    class FailingRuntime:
        async def ainvoke(self, instruction: str) -> AgentRunResult:
            raise RuntimeError("runtime unavailable")

    agent = InvoiceAgent(runtime=FailingRuntime())

    response = await agent.ainvoke("Show invoices.")

    assert response.success is False
    assert "runtime unavailable" in response.content
