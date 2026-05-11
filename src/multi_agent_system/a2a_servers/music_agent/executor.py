from a2a.helpers import new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import Role

from multi_agent_system.a2a_servers.music_agent.agent import MusicAgent


class MusicAgentExecutor(AgentExecutor):
    def __init__(self) -> None:
        self.agent = MusicAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        result = await self.agent.ainvoke(query)

        await event_queue.enqueue_event(
            new_text_message(
                text=result.model_dump_json(indent=2),
                role=Role.ROLE_AGENT,
            )
        )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        raise NotImplementedError("Cancel is not supported by MusicAgentExecutor.")