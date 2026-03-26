# import logging

# from a2a.server.agent_execution import AgentExecutor, RequestContext
# from a2a.server.events import EventQueue
# from a2a.server.tasks import TaskUpdater
# from a2a.types import (
#     DataPart,
#     InvalidParamsError,
#     Part,
#     SendStreamingMessageSuccessResponse,
#     Task,
#     TaskArtifactUpdateEvent,
#     TaskState,
#     TaskStatusUpdateEvent,
#     TextPart,
#     UnsupportedOperationError,
# )
# from a2a.utils import new_agent_text_message, new_task
# from a2a.utils.errors import ServerError
# from a2a_mcp.common.base_agent import BaseAgent


# logger = logging.getLogger(__name__)


# class GenericAgentExecutor(AgentExecutor):
#     """AgentExecutor used by invoice agents and music agent"""

#     def __init__(self, agent: BaseAgent):
#         self.agent = agent

#     async def execute(
#         self,
#         context: RequestContext,
#         event_queue: EventQueue,
#     ) -> None:
#         logger.info(f'Executing agent {self.agent.agent_name}')
#         error = self._validate_request(context)
#         if error:
#             raise ServerError(error=InvalidParamsError())

#         query = context.get_user_input()
#         task = context.current_task
#         if not task:
#             task = new_task(context.message)
#             await event_queue.enqueue_event(task)
#         updater = TaskUpdater(event_queue, task.id, task.context_id)
#         async for item in self.agent.stream(query, task.context_id, task.id):
#             # Agent to Agent call will return events,
#             # Update the relevant ids to proxy back.
#             if hasattr(item, 'root') and isinstance(
#                 item.root, SendStreamingMessageSuccessResponse
#             ):
#                 event = item.root.result
#                 if isinstance(event,(TaskStatusUpdateEvent | TaskArtifactUpdateEvent)):
#                     await event_queue.enqueue_event(event)
#                 continue

#             is_task_complete = item['is_task_complete']
#             require_user_input = item['require_user_input']

#             if is_task_complete:
#                 content = item['content']
#                 if item['response_type'] == 'data' and isinstance(content, dict):
#                     part = Part(root=DataPart(data=content))
#                 else:
#                     # Fallback: if content is a string (or data but not dict), use TextPart
#                     part = Part(root=TextPart(text=str(content)))
 
#                 await updater.add_artifact(
#                     [part],
#                     name=f'{self.agent.agent_name}-result',
#                 )
#                 await updater.complete()
#                 break
#             if require_user_input:
#                 await updater.update_status(
#                     TaskState.input_required,
#                     new_agent_text_message(
#                         item['content'],
#                         task.context_id,
#                         task.id,
#                     ),
#                     final=True,
#                 )
#                 break
#             await updater.update_status(
#                 TaskState.working,
#                 new_agent_text_message(
#                     item['content'],
#                     task.context_id,
#                     task.id,
#                 ),
#             )

#     def _validate_request(self, context: RequestContext) -> bool:
#         return False

#     async def cancel(
#         self, request: RequestContext, event_queue: EventQueue
#     ) -> Task | None:
#         raise ServerError(error=UnsupportedOperationError())

import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    DataPart,
    InvalidParamsError,
    Part,
    SendStreamingMessageSuccessResponse,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatusUpdateEvent,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError
from a2a_mcp.common.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class GenericAgentExecutor(AgentExecutor):
    """AgentExecutor used by invoice agents and music agent"""

    def __init__(self, agent: BaseAgent):
        self.agent = agent

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        logger.info(f'Executing agent: {self.agent.agent_name}')
        error = self._validate_request(context)
        if error:
            raise ServerError(error=InvalidParamsError())

        query = context.get_user_input()
        task = context.current_task

        if not task:
            task = new_task(context.message)

        # ==========================================
        # 🔧 THE FIX: Correct A2A TaskUpdater Initialization
        # ==========================================
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        # Notice how this is no longer indented under an `async with`
        async for item in self.agent.stream(task.description):
            
            # ==========================================
            # 🔍 ACTUAL DEBUGGING LOGIC
            # ==========================================
            logger.debug(f"[{self.agent.agent_name} STREAM DEBUG] Type: {type(item)}")
            logger.debug(f"[{self.agent.agent_name} STREAM DEBUG] Payload: {repr(item)}")

            if not isinstance(item, dict):
                error_msg = (
                    f"\n{'='*60}\n"
                    f"🚨 CRITICAL TYPE ERROR IN AGENT: {self.agent.agent_name} 🚨\n"
                    f"{'='*60}\n"
                    f"The GenericAgentExecutor expects a 'dict' from the stream.\n"
                    f"Instead, it received a '{type(item).__name__}'.\n\n"
                    f"RAW DATA RECEIVED:\n{repr(item)}\n\n"
                    f"HOW TO FIX THIS:\n"
                    f"1. Open the file for '{self.agent.agent_name}'.\n"
                    f"2. Look at the 'stream()' method.\n"
                    f"3. Ensure you are not accidentally yielding a tuple (check for trailing commas!).\n"
                    f"4. If you are yielding raw LangGraph chunks, you must parse them into a dict first.\n"
                    f"{'='*60}\n"
                )
                logger.error(error_msg)
                raise ValueError(f"Agent {self.agent.agent_name} yielded invalid data type: {type(item)}")
            # ==========================================

            is_task_complete = item.get('is_task_complete', False)
            require_user_input = item.get('require_user_input', False)
            response_type = item.get('response_type', 'text')
            content = item.get('content', '')

            if is_task_complete:
                if response_type == 'data' and isinstance(content, dict):
                    part = Part(root=DataPart(data=content))
                else:
                    part = Part(root=TextPart(text=str(content)))
 
                await updater.add_artifact(
                    [part],
                    name=f'{self.agent.agent_name}-result',
                )
                await updater.complete()
                break
            
            if require_user_input:
                await updater.update_status(
                    TaskState.input_required,
                    new_agent_text_message(
                        str(content),
                        task.context_id,
                        task.id,
                    ),
                    final=True,
                )
                break
            
            await updater.update_status(
                TaskState.working,
                new_agent_text_message(
                    str(content),
                    task.context_id,
                    task.id,
                ),
            )

    def _validate_request(self, context: RequestContext) -> bool:
        return False

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())