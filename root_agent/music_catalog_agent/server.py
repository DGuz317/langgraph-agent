import uvicorn
from typing_extensions import override
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage

from music_catalog_agent.agent import build_music_agent

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill, AgentCapabilities
from a2a.utils import new_agent_text_message


class MusicAgentExecutor(AgentExecutor):
    """Bridge between A2A protocol and your LangGraph music agent."""

    def __init__(self):
        self.agent = build_music_agent  # reuse the already-initialized agent

    @override
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query = context.get_user_input()

        result = await self.agent.ainvoke({
            "messages": [HumanMessage(content=query)]
        })
        response = result["messages"][-1].content

        await event_queue.enqueue_event(new_agent_text_message(response))

    @override
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("Cancel not supported")


if __name__ == "__main__":
    agent_card = AgentCard(
        name="Music Catalog Agent",
        description="Retrieves music information including albums, tracks, and songs by genre.",
        url="http://localhost:8011/.well-known/agent-card.json",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[
            AgentSkill(
                id="music_lookup",
                name="Music Lookup",
                description="Find albums by artist, tracks by artist, songs by genre, or check if a song exists",
                tags=["music", "albums", "tracks"],
                examples=["What albums do you have by U2?", "Give me some jazz songs"]
            )
        ]
    )

    request_handler = DefaultRequestHandler(
        agent_executor=MusicAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    uvicorn.run(server.build(), host="localhost", port=8011)