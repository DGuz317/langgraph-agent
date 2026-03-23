import os
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
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

client = MultiServerMCPClient(
    {
        "My-MCP-Server": {
            "transport": "http",
            "url": "http://localhost:8001/mcp",
        }
    }
)

@tool
async def get_invoice_agent(request: str) -> str:
    """
    Consult this tool for any questions regarding customer invoices, unit prices, or 
    assigned support employees. 
    
    Args:
        request: The user's natural language question about invoices.
    """
    async with client.session("My-MCP-Server") as session:
        tools = await load_mcp_tools(session)

        ALLOWED_TOOL_NAMES = {
            "get_invoices_by_customer_sorted_by_date",
            "get_invoices_sorted_by_unit_price",
            "get_employee_by_invoice_and_customer",
        }
        invoice_tools = [t for t in tools if t.name in ALLOWED_TOOL_NAMES]

        agent = create_agent(
            model=llm,
            tools=invoice_tools,
            name="invoice_information_subagent",
            system_prompt=invoice_subagent_prompt,
        )
        final_content = "" 
        
        async for chunk in agent.astream(
            {"messages": [HumanMessage(content=request)]},
            stream_mode="values",
        ):
            if chunk["messages"]:
                last_msg = chunk["messages"][-1]
                last_msg.pretty_print() 
                final_content = last_msg.content

        return final_content