from a2a.helpers import get_data_parts, new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import Role
from pydantic import ValidationError

from multi_agent_system.a2a_servers.invoice_agent.agent import InvoiceAgent
from multi_agent_system.a2a_servers.invoice_agent.schemas import (
    InvoiceAgentResponse,
    InvoiceTaskPayload,
)


class InvoiceAgentExecutor(AgentExecutor):
    def __init__(self) -> None:
        self.agent = InvoiceAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        data_parts = get_data_parts(context.message.parts) if context.message else []

        if data_parts:
            try:
                payload = InvoiceTaskPayload.model_validate(data_parts[0])
            except ValidationError:
                result = InvoiceAgentResponse(
                    success=False,
                    content="Invalid structured invoice request.",
                )
            else:
                result = await self.agent.invoke_request(payload.to_request())
        else:
            result = await self.agent.ainvoke(context.get_user_input())

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
        raise NotImplementedError("Cancel is not supported by InvoiceAgentExecutor.")
