import json
import logging
import os

from collections.abc import AsyncIterable

from a2a.types import (
    SendStreamingMessageSuccessResponse,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatusUpdateEvent,
)
from a2a_mcp.common import prompts
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from a2a_mcp.common.workflow import Status, WorkflowGraph, WorkflowNode
from google import genai
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """Orchestrator Agent."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name='Orchestrator Agent',
            description='Facilitate inter agent communication',
            content_types=['text', 'text/plain'],
        )
        self.graph = None
        self.results = []
        self.store_context = {}
        self.query_history = []
        self.context_id = None

    async def generate_summary(self) -> str:
        client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        # Build results summary from artifacts
        results_text = []
        for artifact in self.results:
            if artifact.name != 'PlannerAgent-result':
                for part in artifact.parts:
                    if hasattr(part.root, 'text'):
                        results_text.append(f'{artifact.name}: {part.root.text}')
                    elif hasattr(part.root, 'data'):
                        results_text.append(f'{artifact.name}: {part.root.data}')

        contents = (
            f'{prompts.SUMMARY_COT_INSTRUCTIONS}\n\n'
            f'Original query: {self.query_history[-1] if self.query_history else ""}\n\n'
            f'Results from agents:\n' + '\n'.join(results_text) if results_text
            else f'Query: {self.query_history[-1] if self.query_history else ""}\n'
                 f'Please provide a helpful response based on the completed tasks.'
        )
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config={'temperature': 0.0},
        )
        return response.text

    def answer_user_question(self, question) -> str:
        try:
            client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
            prompt = (
                f'You are a music store assistant. Based on this conversation history: '
                f'{str(self.query_history)}\n'
                f'And this context: {str(self.store_context)}\n'
                f'Can you answer this question: {question}\n'
                f'Respond in JSON: {{"can_answer": "yes" or "no", "answer": "<your answer>"}}'
            )
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={
                    'temperature': 0.0,
                    'response_mime_type': 'application/json',
                },
            )
            return response.text
        except Exception as e:
            logger.info(f'Error answering user question: {e}')
        return '{"can_answer": "no", "answer": "Cannot answer based on provided context"}'

    def set_node_attributes(
        self, node_id, task_id=None, context_id=None, query=None
    ):
        attr_val = {}
        if task_id:
            attr_val['task_id'] = task_id
        if context_id:
            attr_val['context_id'] = context_id
        if query:
            attr_val['query'] = query

        self.graph.set_node_attributes(node_id, attr_val)

    def add_graph_node(
        self,
        task_id,
        context_id,
        query: str,
        node_id: str = None,
        node_key: str = None,
        node_label: str = None,
    ) -> WorkflowNode:
        """Add a node to the graph."""
        node = WorkflowNode(
            task=query, node_key=node_key, node_label=node_label
        )
        self.graph.add_node(node)
        if node_id:
            self.graph.add_edge(node_id, node.id)
        self.set_node_attributes(node.id, task_id, context_id, query)
        return node

    def clear_state(self):
        self.graph = None
        self.results.clear()
        self.store_context.clear()
        self.query_history.clear()

    async def stream(self, query, context_id, task_id) -> AsyncIterable[dict[str, any]]:
        """Execute and stream response."""
        logger.info(
            f'Running {self.agent_name} stream for session {context_id}, task {task_id} - {query}'
        )
        if not query:
            raise ValueError('Query cannot be empty')
        if self.context_id != context_id:
            # Clear state when the context changes
            self.clear_state()
            self.context_id = context_id

        self.query_history.append(query)
        start_node_id = None
        # Graph does not exist, start a new graph with planner node.
        if not self.graph:
            self.graph = WorkflowGraph()
            planner_node = self.add_graph_node(
                task_id=task_id,
                context_id=context_id,
                query=query,
                node_key='planner',
                node_label='Planner',
            )
            start_node_id = planner_node.id
        # Paused state is when the agent might need more information.
        elif self.graph.state == Status.PAUSED:
            start_node_id = self.graph.paused_node_id
            self.set_node_attributes(node_id=start_node_id, query=query)

        # This loop can be avoided if the workflow graph is dynamic or
        # is built from the results of the planner when the planner
        # iself is not a part of the graph.
        # TODO: Make the graph dynamically iterable over edges
        while True:
            # Set attributes on the node so we propagate task and context
            self.set_node_attributes(
                node_id=start_node_id,
                task_id=task_id,
                context_id=context_id,
            )
            # Resume workflow, used when the workflow nodes are updated.
            should_resume_workflow = False
            async for chunk in self.graph.run_workflow(
                start_node_id=start_node_id
            ):
                # ✅ FIX: New SDK yields (Task, event) tuples — extract the event
                a2a_event = None
                if isinstance(chunk, tuple):
                    for element in chunk:
                        if isinstance(element, TaskArtifactUpdateEvent):
                            a2a_event = element
                            break
                        if isinstance(element, TaskStatusUpdateEvent):
                            a2a_event = element
                            break
                elif isinstance(chunk, (TaskArtifactUpdateEvent, TaskStatusUpdateEvent)):
                    a2a_event = chunk
                elif isinstance(chunk, SendStreamingMessageSuccessResponse):
                    a2a_event = chunk.result

                if isinstance(a2a_event, TaskStatusUpdateEvent):
                    task_status_event = a2a_event
                    context_id = task_status_event.context_id
                    if (
                        task_status_event.status.state == TaskState.completed
                        and context_id
                    ):
                        continue
                    if task_status_event.status.state == TaskState.input_required:
                        question = task_status_event.status.message.parts[0].root.text
                        try:
                            answer = json.loads(self.answer_user_question(question))
                            logger.info(f'Agent Answer {answer}')
                            if answer['can_answer'] == 'yes':
                                query = answer['answer']
                                start_node_id = self.graph.paused_node_id
                                self.set_node_attributes(
                                    node_id=start_node_id, query=query
                                )
                                should_resume_workflow = True
                        except Exception:
                            logger.info('Cannot convert answer data')

                elif isinstance(a2a_event, TaskArtifactUpdateEvent):
                    artifact = a2a_event.artifact
                    self.results.append(artifact)
                    if artifact.name == 'PlannerAgent-result':
                        root_part = artifact.parts[0].root
                        
                        # Safely extract data whether the SDK sent a DataPart or TextPart
                        if hasattr(root_part, 'data'):
                            artifact_data = root_part.data
                        elif hasattr(root_part, 'text'):
                            if isinstance(root_part.text, str) and root_part.text.strip():
                                try:
                                    # Try to parse the text as JSON
                                    artifact_data = json.loads(root_part.text)
                                except json.JSONDecodeError:
                                    logger.error(f"PlannerAgent returned invalid JSON: {root_part.text}")
                                    continue # Skip this artifact since we can't read the tasks
                            else:
                                artifact_data = {"tasks": []} # Fallback for empty text
                        else:
                            logger.error("Unknown part type received from PlannerAgent")
                            continue

                        logger.info(
                            f'Updating workflow with {len(artifact_data.get("tasks", []))} task nodes'
                        )
                        current_node_id = start_node_id
                        for idx, task_data in enumerate(artifact_data['tasks']):
                            task_query = task_data.get('query') or task_data.get('description', '')
                            task_agent = task_data.get('agent', '')
                            node = self.add_graph_node(
                                task_id=task_id,
                                context_id=context_id,
                                query=task_query,
                                node_id=current_node_id,
                                node_label=task_agent,
                            )
                            current_node_id = node.id
                            if idx == 0:
                                should_resume_workflow = True
                                start_node_id = node.id
                    else:
                        # Artifact from sub-agent — store result, don't yield
                        logger.info(f'Sub-agent artifact received: {artifact.name}')
                        continue

                # When the workflow needs to be resumed, do not yield partial.
                if not should_resume_workflow:
                    logger.info('No workflow resume detected, yielding chunk')
                    yield chunk

            # The graph is complete and no updates, so okay to break from the loop.
            if not should_resume_workflow:
                logger.info('Workflow iteration complete. Exiting main loop.')
                break
            else:
                logger.info('Restarting workflow loop.')

        logger.info(f'Graph state after loop: {self.graph.state}')
        if self.graph.state == Status.COMPLETED:
            logger.info(f'Generating summary for {len(self.results)} results')
            try:
                summary = await self.generate_summary()
            except Exception as e:
                logger.error(f'Error generating summary: {e}')
                summary = f'Tasks completed. Results: {str(self.results)}'
            self.clear_state()
            logger.info(f'Summary generated: {summary[:100]}...')
            yield {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': summary,
            }
        else:
            logger.warning(f'Workflow ended in non-completed state: {self.graph.state}')
            yield {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': 'Tasks completed but no summary could be generated.',
            }