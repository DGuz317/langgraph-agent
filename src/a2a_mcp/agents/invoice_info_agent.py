import logging
import asyncio

from collections.abc import AsyncIterable
from typing import Any, Literal

from a2a_mcp.common import prompts
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.types import TaskList
from a2a_mcp.common.utils import init_api_key
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent
from pydantic import BaseModel

memory = MemorySaver()
logger = logging.getLogger(__name__)

ALLOWED_TOOL_NAMES = {
    "get_invoices_by_customer_sorted_by_date",
    "get_invoices_sorted_by_unit_price",
    "get_employee_by_invoice_and_customer",
}


class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str


class InvoiceAgent(BaseAgent):
    """InvoiceAgent - specialized for retrieving and processing invoice information.""" 

    async def fetch_mcp_tools(self) -> list:
        client = MultiServerMCPClient(
                {
                    "My-MCP-Server": {
                        "transport": "streamable_http",
                        "url": "http://localhost:10000/mcp",
                    }
                }
            )
        tools = await client.get_tools() 
        invoice_tools = [t for t in tools if t.name in ALLOWED_TOOL_NAMES]
        logger.info(f"Allowed tools from MCP Server: {invoice_tools}")
        return invoice_tools

    def __init__(self):
        init_api_key()
        logger.info('Initializing InvoiceAgent')
        super().__init__(
            agent_name='InvoiceAgent',
            description='Retrieving and processing invoice information',
            content_types=['text', 'text/plain'],
        )
        self.model = ChatGoogleGenerativeAI(model='gemini-2.5-flash')
        # graph is built lazily in stream/invoke after async tool fetch
        self.graph = None
    
    async def _ensure_graph(self):
        if self.graph is None:
            tools = await self.fetch_mcp_tools()
            self.graph = create_agent(
                self.model,
                tools=tools,
                checkpointer=memory,
                system_prompt=prompts.INVOICE_AGENT_PROMPT,
                response_format=ResponseFormat,
            )

    async def invoke(self, query, sessionId) -> str:
        await self._ensure_graph()
        config = {'configurable': {'thread_id': sessionId}}
        await self.graph.ainvoke({'messages': [('user', query)]}, config)
        return self.get_agent_response(config)

    async def stream(self, query, sessionId, task_id) -> AsyncIterable[dict[str, Any]]:
        await self._ensure_graph()
        inputs = {'messages': [('user', query)]}
        config = {'configurable': {'thread_id': sessionId}}

        logger.info(f'Running InvoiceAgent stream for session {sessionId} {task_id} with input {query}')

        async for item in self.graph.astream(inputs, config, stream_mode='values'):
            message = item['messages'][-1]
            if isinstance(message, AIMessage) and message.tool_calls:
                yield {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Looking up invoice information...',
                }
            elif isinstance(message, ToolMessage):
                yield {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Processing invoice data...',
                }
        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(structured_response, ResponseFormat):
            if (structured_response.status == 'input_required'):
                return {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message,
                }
            if structured_response.status == 'error':
                return {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message,
                }
            if structured_response.status == 'completed':
                return {
                    'response_type': 'data',
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.message,
                }
        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': 'We are unable to process your request at the moment. Please try again.',
        }
