import uvicorn
import os
from typing_extensions import override
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from dotenv import load_dotenv
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill, AgentCapabilities
from a2a.utils import new_agent_text_message
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
from invoice_subagent_prompt import invoice_subagent_prompt
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

class InvoiceAgentExecutor(AgentExecutor):
    def __init__(self):
        self.client = MultiServerMCPClient({
            "My-MCP-Server": {
                "transport": "http",
                "url": "http://localhost:8001/mcp",
            }
        })
        self.llm = llm
        self.prompt = invoice_subagent_prompt

    @override
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query = context.get_user_input()

        async with self.client.session("My-MCP-Server") as session:
            tools = await load_mcp_tools(session)
            ALLOWED_TOOL_NAMES = {
                "get_invoices_by_customer_sorted_by_date",
                "get_invoices_sorted_by_unit_price",
                "get_employee_by_invoice_and_customer"
            }
            invoice_tools = [t for t in tools if t.name in ALLOWED_TOOL_NAMES]

            agent = create_agent(
                model=self.llm,
                tools=invoice_tools,
                name="invoice_information_subagent",
                system_prompt=self.prompt,
            )
            final_content = ""
            async for chunk in agent.astream(
                {"messages": [HumanMessage(content=query)]},
                stream_mode="values",
            ):
                if chunk["messages"]:
                    final_content = chunk["messages"][-1].content

        await event_queue.enqueue_event(new_agent_text_message(final_content))
        
    @override
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("Cancel not supported")

if __name__ == "__main__":
    agent_card = AgentCard(
        name="Invoice Information Agent",
        description="Retrieves invoice information for customers using natural language.",
        url="http://localhost:8010/.well-known/agent-card.json",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[
            AgentSkill(
                id="invoice_lookup",
                name="Invoice Lookup",
                description="Look up invoices by date, unit price, or find associated employee",
                tags=["invoice", "billing"],
                examples=["My customer ID is 1. What was my most recent invoice?"]
            )
        ]
    )

    request_handler = DefaultRequestHandler(
        agent_executor=InvoiceAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    uvicorn.run(server.build(), host="localhost", port=8010)