import os
import sys
import ast

from collections.abc import AsyncIterable
from typing import Any, Literal, ClassVar

import httpx

from a2a_mcp.common import prompts
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.types import TaskList
from a2a_mcp.common.utils import init_api_key
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent
from pydantic import BaseModel
from dotenv import load_dotenv
import logging

memory = MemorySaver()
logger = logging.getLogger(__name__)

# sys.path.insert(1, r'C:/Users/nvdung1/Desktop/langraph_agent/database')
# import get_database
# db = get_database.db 

# @tool
# def get_invoices_by_customer_sorted_by_date(customer_id: str) -> list[dict]:
#     """
#     Look up all invoices for a customer using their ID.
#     The invoices are sorted in descending order by invoice date, which helps when the customer wants to view their most recent/oldest invoice, or if 
#     they want to view invoices within a specific date range.
    
#     Args:
#         customer_id (str): customer_id, which serves as the identifier.
    
#     Returns:
#         list[dict]: A list of invoices for the customer.
#     """
#     # Executes a SQL query to retrieve all invoice details for a given customer ID,
#     # ordered by invoice date in descending order (most recent first).
#     result = db.run(
#         f"SELECT * FROM Invoice WHERE CustomerId = {customer_id} ORDER BY InvoiceDate DESC;",
#         include_columns=True 
#     )
#     if not result:
#         return []
#     return ast.literal_eval(result)

# @tool
# def get_invoices_sorted_by_unit_price(customer_id: str) -> list[dict]:
#     """
#     Use this tool when the customer wants to know the details of one of their invoices based on the unit price/cost of the invoice.
#     This tool looks up all invoices for a customer, and sorts the unit price from highest to lowest. In order to find the invoice associated with the customer, 
#     we need to know the customer ID.
    
#     Args:
#         customer_id (str): customer_id, which serves as the identifier.
    
#     Returns:
#         list[dict]: A list of invoices sorted by unit price.
#     """
#     # Executes a SQL query to retrieve invoice details along with the unit price of items in those invoices,
#     # for a given customer ID, ordered by unit price in descending order (highest unit price first).
#     query = f"""
#         SELECT Invoice.*, InvoiceLine.UnitPrice
#         FROM Invoice
#         JOIN InvoiceLine ON Invoice.InvoiceId = InvoiceLine.InvoiceId
#         WHERE Invoice.CustomerId = {customer_id}
#         ORDER BY InvoiceLine.UnitPrice DESC;
#     """
#     result = db.run(query, include_columns=True)  # ✅ add include_columns
#     if not result:
#         return []
#     return ast.literal_eval(result)

# @tool
# def get_employee_by_invoice_and_customer(invoice_id: str, customer_id: str) -> dict:
#     """
#     This tool will take in an invoice ID and a customer ID and return the employee information associated with the invoice.

#     Args:
#         invoice_id (int): The ID of the specific invoice.
#         customer_id (str): customer_id, which serves as the identifier.

#     Returns:
#         dict: Information about the employee associated with the invoice.
#     """

#     # Executes a SQL query to find the employee associated with a specific invoice and customer.
#     # It joins Employee, Customer, and Invoice tables to retrieve employee first name, title, and email.
#     query = f"""
#         SELECT Employee.FirstName, Employee.Title, Employee.Email
#         FROM Employee
#         JOIN Customer ON Customer.SupportRepId = Employee.EmployeeId
#         JOIN Invoice ON Invoice.CustomerId = Customer.CustomerId
#         WHERE Invoice.InvoiceId = ({invoice_id}) AND Invoice.CustomerId = ({customer_id});
#     """
#     result = db.run(query, include_columns=True)
#     if not result:
#         return {"error": f"No employee found for invoice ID {invoice_id} and customer ID {customer_id}."}
    
#     parsed = ast.literal_eval(result)
#     return parsed[0] if isinstance(parsed, list) else parsed


class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str


class InvoiceAgent(BaseAgent):
    """InvoiceAgent - specialized for retrieving and processing invoice information.""" 

    def __init__(self):
        init_api_key()

        logger.info('Initializing InvoiceAgent')

        super().__init__(
            agent_name='InvoiceAgent',
            description='Retrieving and processing invoice information',
            content_types=['text', 'text/plain'],
        )

        self.model = ChatGoogleGenerativeAI(
            model='gemini-2.5-flash'
        )

        self.tools = [get_employee_by_invoice_and_customer, 
                        get_invoices_sorted_by_unit_price, 
                        get_invoices_by_customer_sorted_by_date]

        self.graph = create_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            system_prompt=prompts.INVOICE_AGENT_PROMPT,
            response_format=ResponseFormat,
        )
    
    def invoke(self, query, sessionId) -> str:
        config = {'configurable': {'thread_id': sessionId}}
        self.graph.invoke({'messages': [('user', query)]}, config)
        return self.get_agent_response(config)

    async def stream(self, query, sessionId, task_id) -> AsyncIterable[dict[str, Any]]:
        inputs = {'messages': [('user', query)]}
        config = {'configurable': {'thread_id': sessionId}}

        logger.info(f'Running InvoiceAgent stream for session {sessionId} {task_id} with input {query}')

        for item in self.graph.stream(inputs, config, stream_mode='values'):
            message = item['messages'][-1]
            if isinstance(message, AIMessage):
                yield {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': message.content,
                }
        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(
            structured_response, ResponseFormat
        ):
            if (
                structured_response.status == 'input_required'
                # and structured_response.content.tasks
            ):
                return {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.question,
                }
            if structured_response.status == 'error':
                return {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.question,
                }
            if structured_response.status == 'completed':
                return {
                    'response_type': 'data',
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.content.model_dump(),
                }
        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': 'We are unable to process your request at the moment. Please try again.',
        }

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     google_api_key=os.getenv("GOOGLE_API_KEY"),
# )

# client = MultiServerMCPClient(
#     {
#         "My-MCP-Server": {
#             "transport": "http",
#             "url": "http://localhost:8001/mcp",
#         }
#     }
# )

# ALLOWED_TOOL_NAMES = {
#     "get_invoices_by_customer_sorted_by_date",
#     "get_invoices_sorted_by_unit_price",
#     "get_employee_by_invoice_and_customer",
# }
# invoice_tools = [t for t in tools if t.name in ALLOWED_TOOL_NAMES]