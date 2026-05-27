from a2a.helpers import get_data_parts, new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import Role
from pydantic import ValidationError

from multi_agent_system.a2a_servers.music_agent.agent import MusicAgent
from multi_agent_system.a2a_servers.music_agent.schemas import (
    MusicAgentResponse,
    MusicTaskPayload,
)
from multi_agent_system.common.execution_evidence import collect_execution_evidence


class MusicAgentExecutor(AgentExecutor):
    def __init__(self) -> None:
        self.agent = MusicAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        data_parts = get_data_parts(context.message.parts) if context.message else []

        with collect_execution_evidence() as evidence:
            if data_parts:
                try:
                    payload = MusicTaskPayload.model_validate(data_parts[0])
                except ValidationError:
                    result = MusicAgentResponse(
                        success=False,
                        content="Invalid structured music request.",
                    )
                else:
                    result = await self.agent.invoke_request(payload.to_request())
            else:
                result = await self.agent.ainvoke(context.get_user_input())

        result = result.model_copy(
            update={"execution_evidence": [*result.execution_evidence, *evidence]}
        )

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
