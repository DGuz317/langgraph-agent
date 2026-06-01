from a2a.helpers import get_data_parts, new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import Role

from multi_agent_system.a2a_servers.invoice_agent.agent import InvoiceAgent
from multi_agent_system.common.execution_evidence import collect_execution_evidence


class InvoiceAgentExecutor(AgentExecutor):
    def __init__(self) -> None:
        self.agent = InvoiceAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        data_parts = get_data_parts(context.message.parts) if context.message else []

        with collect_execution_evidence() as evidence:
            result = await self.agent.ainvoke(
                _instruction_from_context(context, data_parts)
            )

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
        raise NotImplementedError("Cancel is not supported by InvoiceAgentExecutor.")


def _instruction_from_context(
    context: RequestContext,
    data_parts: list[dict],
) -> str:
    if data_parts and isinstance(data_parts[0], dict):
        instruction = data_parts[0].get("instruction")
        if isinstance(instruction, str) and instruction.strip():
            return instruction.strip()

    return context.get_user_input()
