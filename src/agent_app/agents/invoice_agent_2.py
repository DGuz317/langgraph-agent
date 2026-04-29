import os
import ast 
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict, Any

from langchain_community.utilities import SQLDatabase
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama

from agent_app.common.prompts import INVOICE_AGENT_PROMPT


load_dotenv()
checkpointer = InMemorySaver()


# --- Databases ---
db = SQLDatabase.from_uri("sqlite:////home/nvdung1/Desktop/MultiAgentSystem/langgraph-agent/src/agent_app/database/chinook.db")

# --- Tools ---
@tool()
def get_invoices_by_customer_sorted_by_date(customer_id: str) -> list[dict]:
    """
    Look up all invoices for a customer using their ID.
    The invoices are sorted in descending order by invoice date, which helps when the customer wants to view their most recent/oldest invoice, or if 
    they want to view invoices within a specific date range.
    
    Args:
        customer_id (str): customer_id, which serves as the identifier.
    
    Returns:
        list[dict]: A list of invoices for the customer.
    """
    result = db.run(
        f"SELECT * FROM Invoice WHERE CustomerId = {customer_id} ORDER BY InvoiceDate DESC;",
        include_columns=True
    )
    if not result:
        return []
    return ast.literal_eval(result)

@tool()
def get_invoices_sorted_by_unit_price(customer_id: str) -> list[dict]:
    """
    Use this tool when the customer wants to know the details of one of their invoices based on the unit price/cost of the invoice.
    This tool looks up all invoices for a customer, and sorts the unit price from highest to lowest. In order to find the invoice associated with the customer, 
    we need to know the customer ID.
    
    Args:
        customer_id (str): customer_id, which serves as the identifier.
    
    Returns:
        list[dict]: A list of invoices sorted by unit price.
    """
    query = f"""
        SELECT Invoice.*, InvoiceLine.UnitPrice
        FROM Invoice
        JOIN InvoiceLine ON Invoice.InvoiceId = InvoiceLine.InvoiceId
        WHERE Invoice.CustomerId = {customer_id}
        ORDER BY InvoiceLine.UnitPrice DESC;
    """
    result = db.run(query, include_columns=True)
    if not result:
        return []
    return ast.literal_eval(result)

@tool()
def get_employee_by_invoice_and_customer(invoice_id: str, customer_id: str) -> dict:
    """
    This tool will take in an invoice ID and a customer ID and return the employee information associated with the invoice.

    Args:
        invoice_id (int): The ID of the specific invoice.
        customer_id (str): customer_id, which serves as the identifier.

    Returns:
        dict: Information about the employee associated with the invoice.
    """
    query = f"""
        SELECT Employee.FirstName, Employee.Title, Employee.Email
        FROM Employee
        JOIN Customer ON Customer.SupportRepId = Employee.EmployeeId
        JOIN Invoice ON Invoice.CustomerId = Customer.CustomerId
        WHERE Invoice.InvoiceId = ({invoice_id}) AND Invoice.CustomerId = ({customer_id});
    """
    result = db.run(query, include_columns=True)
    if not result:
        return {"error": f"No employee found for invoice ID {invoice_id} and customer ID {customer_id}."}
    
    parsed = ast.literal_eval(result)
    return parsed[0] if isinstance(parsed, list) else parsed

# --- Connect MCP tools ---


class ResponseFormat(BaseModel):
    """Response to user using this format"""
    status: Literal["input_required", "completed", "failed"] = Field(..., description="The current state of the agent's execution loop.")
    task_id: str = Field(..., description="The specific task or query the agent was asked to process.") 
    answer: str = Field(None, description="The generated response or tool output.")
    confidence: float = Field(..., description="Confident score of the answer.", ge=0, le=1)


MODEL = init_chat_model(
    model=os.getenv("LLM_MODEL"),
    model_provider="ollama",
    base_url=os.getenv("OLLAMA_API_URL"),
    temperature=0,
    timeout=300,
    max_tokens=25000,
)

invoice_agent = create_agent(
    model=MODEL,
    tools=[
        get_invoices_by_customer_sorted_by_date,
        get_invoices_sorted_by_unit_price,
        get_employee_by_invoice_and_customer
    ],
    system_prompt=INVOICE_AGENT_PROMPT,
    response_format=ResponseFormat,
    checkpointer=checkpointer,
)

# --- Simple test ---
# agent_result = invoice_agent.invoke(
#     {"messages": [{"role": "user", "content": "My customer id is 1. What is my latest invoice?"}]},
#     config={"configurable": {"thread_id": "1"}},
# )

# print(agent_result["messages"][-1].content_blocks)
