import asyncio

from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict, Any

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

from agent_app.common.prompts import INVOICE_AGENT_PROMPT


# --- Defined Response Format ---
class ResponseFormat(BaseModel):
    """Response to user using this format"""
    status: Literal["input_required", "completed", "failed"] = Field(..., description="The current state of the agent's execution loop.")
    task_id: str = Field(..., description="The specific task or query the agent was asked to process.") 
    answer: str = Field(None, description="The generated response or tool output.")
    confidence: float = Field(..., description="Confident score of the answer.", ge=0, le=1)


# --- Allowed Tools ---
ALLOWED_TOOL_NAMES = {
    "get_invoices_by_customer_sorted_by_date",
    "get_invoices_sorted_by_unit_price",
    "get_employee_by_invoice_and_customer",
}

# --- Build Agent ---
async def build_invoice_agent(session, model, checkpointer):
    tools = await load_mcp_tools(session)
    invoice_tools = [t for t in tools if t.name in ALLOWED_TOOL_NAMES]

    return create_agent(
        model=model,
        tools=invoice_tools,
        system_prompt=INVOICE_AGENT_PROMPT,
        response_format=ResponseFormat,
        checkpointer=checkpointer,
    )
