import pytest

from multi_agent_system.a2a_servers.music_agent.agent import MusicAgent
from multi_agent_system.common.agent_runtime import AgentRunResult


class RecordingRuntime:
    def __init__(self, result: AgentRunResult | None = None) -> None:
        self.instructions: list[str] = []
        self.result = result or AgentRunResult(
            success=True,
            content="Music answer.",
        )

    async def ainvoke(self, instruction: str) -> AgentRunResult:
        self.instructions.append(instruction)
        return self.result


@pytest.mark.anyio
async def test_music_agent_delegates_instruction_to_runtime() -> None:
    runtime = RecordingRuntime()
    agent = MusicAgent(runtime=runtime)

    response = await agent.ainvoke("Recommend 5 Jazz songs.")

    assert response.success is True
    assert response.content == "Music answer."
    assert runtime.instructions == ["Recommend 5 Jazz songs."]


@pytest.mark.anyio
async def test_music_agent_returns_runtime_failure() -> None:
    class FailingRuntime:
        async def ainvoke(self, instruction: str) -> AgentRunResult:
            raise RuntimeError("runtime unavailable")

    agent = MusicAgent(runtime=FailingRuntime())

    response = await agent.ainvoke("Recommend songs.")

    assert response.success is False
    assert "runtime unavailable" in response.content
