import os
import asyncio
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict, Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from agent_app.common.prompts import INVOICE_AGENT_PROMPT


load_dotenv()
checkpointer = InMemorySaver()


# --- Defined Response Format ---
class ResponseFormat(BaseModel):
    """Response to user using this format"""
    status: Literal["input_required", "completed", "failed"] = Field(..., description="The current state of the agent's execution loop.")
    task_id: str = Field(..., description="The specific task or query the agent was asked to process.") 
    answer: str = Field(None, description="The generated response or tool output.")
    confidence: float = Field(..., description="Confident score of the answer.", ge=0, le=1)


MODEL = init_chat_model(
    model=os.getenv("LLM_MODEL"),
    model_provider=os.getenv("MODEL_PROVIDER"),
    base_url=os.getenv("OLLAMA_API_URL"),
    temperature=0,
    timeout=300,
    max_tokens=25000,
)

# --- Allowed Tools ---
ALLOWED_TOOL_NAMES = {
    "get_invoices_by_customer_sorted_by_date",
    "get_invoices_sorted_by_unit_price",
    "get_employee_by_invoice_and_customer",
}


invoice_agent = None 
client = None 

# --- Connect MCP Server ---
async def init_invoice_agent():
    global invoice_agent, client

    client = MultiServerMCPClient(
        {
            "data_tools": {
                    "transport": "streamable-http",
                    "url": "http://localhost:10000/mcp"
            }
        }
    )

    tools = await client.get_tools()
    invoice_tools = [t for t in tools if t.name in ALLOWED_TOOL_NAMES]
    invoice_agent = create_agent(
        model=MODEL,
        tools=invoice_tools,
        system_prompt=INVOICE_AGENT_PROMPT,
        response_format=ResponseFormat,
        checkpointer=checkpointer,
    )

    return invoice_agent

# --- Simple test ---
# async def _test():
#     await init_invoice_agent()
#     result = await invoice_agent.ainvoke(
#         {"messages": [{"role": "user", "content": "My customer id is 1. What is my latest invoice?"}]},
#         config={"configurable": {"thread_id": "test-1"}},
#     )
#     print(result["structured_response"])


# if __name__ == "__main__":
#     asyncio.run(_test())