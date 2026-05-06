import pytest_asyncio
from agent_app.orchestrator.runtime import AgentRuntime


@pytest_asyncio.fixture(scope="session")
async def runtime():
    rt = AgentRuntime()
    await rt.start()
    yield rt


@pytest_asyncio.fixture(scope="session")
async def agents(runtime):
    return runtime.agents