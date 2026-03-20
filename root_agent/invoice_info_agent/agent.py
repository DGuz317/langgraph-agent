import os
import uuid
import logging
import asyncio
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_google_genai import ChatGoogleGenerativeAI
from .invoice_subagent_prompt import invoice_subagent_prompt
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage

logger = logging.getLogger(__name__)
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

ALLOWED_TOOL_NAMES = {
    "get_invoices_by_customer_sorted_by_date",
    "get_invoices_sorted_by_unit_price",
    "get_employee_by_invoice_and_customer",
}

client = MultiServerMCPClient(
    {
        "My-MCP-Server": {
            "transport": "http",
            "url": "http://localhost:8001/mcp",
        }
    }
)

# ── Initialize agent ──────────────────────────────────────

async def build_invoice_agent():
    async with client.session("My-MCP-Server") as session:
        tools = await load_mcp_tools(session)
        invoice_tools = [t for t in tools if t.name in ALLOWED_TOOL_NAMES]

        agent = create_agent(
            model=llm,
            tools=invoice_tools,
            name="invoice_information_subagent",
            system_prompt=invoice_subagent_prompt,
        )

        logger.info("✅ Invoice agent ready with persistent MCP session")
        yield agent


# ── Subagent exposed as a tool ─────────────────────────────────────────────────

@tool
async def get_invoice_information(request: str) -> str:
    """Get invoice information using natural language.

    Use this when the user wants to retrieve invoice information.
    Handles: invoices sorted by date, invoices sorted by unit price,
    and employee info associated with an invoice and customer.

    Input: Natural language request (e.g., 'My customer id is 1. What was my most recent invoice?')
    """
    async for agent in build_invoice_agent():
        result = await agent.ainvoke({
            "messages": [HumanMessage(content=request)]
        })
        return result["messages"][-1].content


# ── Debug entrypoint ───────────────────────────────────────────────────────────

# async def run_debug():
#     query = "My customer id is 1. What was my most recent invoice, and who was the employee that helped me with it?"
#     config = {"configurable": {"thread_id": str(uuid.uuid4())}}

#     async for agent in build_invoice_agent():
#         async for chunk in agent.astream(
#             {"messages": [HumanMessage(content=query)]},
#             config,
#             stream_mode="values",
#         ):
#             chunk["messages"][-1].pretty_print()


# if __name__ == "__main__":
#     asyncio.run(run_debug())