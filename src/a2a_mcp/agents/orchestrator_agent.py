import logging
import os
import httpx
from uuid import uuid4
from collections.abc import AsyncIterable
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

from a2a.client import ClientFactory, ClientConfig
from a2a.types import Message, Part, TextPart, Role

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class SubAgentTask(BaseModel):
    agent_name: str = Field(
        description="The name of the agent to call (e.g., 'music_catalog_agent', 'invoice_info_agent')"
    )
    query: str = Field(
        description="The specific query to send to this agent"
    )


class RoutingDecision(BaseModel):
    tasks: list[SubAgentTask] = Field(
        description="List of sub-agents to query. Can be empty if the orchestrator can answer directly."
    )


ROUTING_PROMPT = """
You are the Orchestrator for a digital music store. You have two sub-agents:
1. music_catalog_agent: Use for tracks, artists, albums, and genres.
2. invoice_info_agent: Use for invoices, billing, and customer purchases.

Analyze the user's request. Decide which agent(s) need to be queried and what exactly to ask them.
User Request: {user_query}
"""


AGENT_DIRECTORY = {
    'music_catalog_agent': 'http://localhost:8020',
    'invoice_info_agent':  'http://localhost:8010',
}


class OrchestratorAgent(BaseAgent):
    """A standalone Orchestrator that dynamically routes queries to sub-agents."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name='Orchestrator Agent',
            description='Main entry point. Analyzes queries and coordinates with specialized sub-agents.',
            content_types=['text', 'text/plain'],
        )

    async def _determine_routing(self, user_query: str) -> RoutingDecision:
        """Uses Gemini to decide which sub-agents to call."""
        prompt = ROUTING_PROMPT.format(user_query=user_query)
        client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RoutingDecision,
            ),
        )
        return RoutingDecision.model_validate_json(response.text)

    async def _call_sub_agent(self, agent_name: str, query: str) -> str:
        """Connects to a remote A2A sub-agent and returns its final answer."""

        url = AGENT_DIRECTORY.get(agent_name)
        if not url:
            return f"Error: Agent '{agent_name}' not found in directory."

        custom_http = httpx.AsyncClient(timeout=300.0)
        config     = ClientConfig(httpx_client=custom_http)

        try:
            logger.info(f"[{agent_name}] Connecting to {url} ...")
            client = await ClientFactory.connect(url, client_config=config)
            logger.info(f"[{agent_name}] Connected. Client type: {type(client).__name__}")
            request_message = Message(
                role=Role.user,
                messageId=uuid4().hex,
                parts=[Part(root=TextPart(text=query))]
            )
            logger.info(f"[{agent_name}] Sending query: {query[:120]}")

            artifact_texts      = []   
            final_status_texts  = []   
            event_count         = 0

            async for raw_event in client.send_message(request_message):
                event_count += 1
                if isinstance(raw_event, tuple) and len(raw_event) == 2:
                    _task_snapshot, event_obj = raw_event
                else:
                    event_obj = raw_event

                event_type = type(event_obj).__name__
                logger.info(f"[{agent_name}] Event #{event_count}: {event_type}")

                if hasattr(event_obj, 'artifact') and event_obj.artifact:
                    artifact = event_obj.artifact
                    if hasattr(artifact, 'parts'):
                        for part in artifact.parts:
                            text = _extract_text(part)
                            if text:
                                artifact_texts.append(text)
                                logger.info(f"[{agent_name}] ✅ Artifact text: {text[:120]}")

                elif hasattr(event_obj, 'status') and event_obj.status:
                    status = event_obj.status
                    state  = str(getattr(status, 'state', ''))
                    logger.info(f"[{agent_name}] Status state: {state}")

                    if 'completed' in state.lower():
                        msg = getattr(status, 'message', None)
                        if msg and hasattr(msg, 'parts'):
                            for part in msg.parts:
                                text = _extract_text(part)
                                if text:
                                    final_status_texts.append(text)
                                    logger.info(f"[{agent_name}] ✅ Completed status text: {text[:120]}")

            logger.info(f"[{agent_name}] Loop done. {event_count} events received.")
            logger.info(f"[{agent_name}] artifact_texts:     {artifact_texts}")
            logger.info(f"[{agent_name}] final_status_texts: {final_status_texts}")

            best = artifact_texts if artifact_texts else final_status_texts
            result = "\n".join(best).strip()

            if result:
                logger.info(f"[{agent_name}] Returning result: {result[:200]}")
            else:
                logger.warning(f"[{agent_name}] ⚠️  No content collected – returning empty message.")

            return result if result else "No content returned from agent."

        except Exception as e:
            logger.error(
                f"[{agent_name}] ❌ Exception: {type(e).__name__}: {e}",
                exc_info=True
            )
            return f"I couldn't reach the {agent_name.replace('_', ' ')} right now."

    async def _generate_summary(self, user_query: str, results: list[str]) -> str:
        """Asks Gemini to synthesise a final answer from sub-agent responses."""
        if not results:
            return "I couldn't gather any information to answer that request."

        context = "\n\n".join(results)
        prompt  = f"""
        User Question: {user_query}

        Information gathered from sub-agents:
        {context}

        Please provide a clear, helpful, and comprehensive response to the user
        based ONLY on the information provided above.
        """
        client   = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text

    async def stream(self, query: str, context_id: str) -> AsyncIterable[dict]:
        """Main execution stream: route → execute → synthesise."""

        logger.info(f"OrchestratorAgent stream started | session={context_id} | query={query}")

        try:
            logger.info("Phase 1: Determining routing strategy ...")
            routing_decision = await self._determine_routing(query)

            if not routing_decision.tasks:
                yield {
                    'response_type': 'text',
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': "I don't need any sub-agents for this. How can I help you?",
                }
                return

            logger.info(f"Phase 2: Executing {len(routing_decision.tasks)} sub-agent task(s) ...")
            agent_results = []

            for task in routing_decision.tasks:
                logger.info(f"  → Delegating to [{task.agent_name}]: {task.query}")

                yield {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': f"Checking with {task.agent_name.replace('_', ' ')}...",
                }

                result_text = await self._call_sub_agent(task.agent_name, task.query)
                agent_results.append(
                    f"--- Response from {task.agent_name} ---\n{result_text}"
                )
                logger.info(f"  ← [{task.agent_name}] returned {len(result_text)} chars")

            logger.info("Phase 3: Synthesising final response ...")
            yield {
                'response_type':    'text',
                'is_task_complete': False,
                'require_user_input': False,
                'content': "Compiling the final answer...",
            }

            final_summary = await self._generate_summary(query, agent_results)
            logger.info("Phase 3: Summary generated successfully.")

            yield {
                'response_type':    'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': final_summary,
            }

        except Exception as e:
            logger.error(f"OrchestratorAgent error: {e}", exc_info=True)
            yield {
                'response_type':    'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f"An error occurred while orchestrating the response: {e}",
            }


def _extract_text(part) -> str:
    """Safely pull .root.text out of an A2A Part object."""
    try:
        return part.root.text or ""
    except AttributeError:
        return ""