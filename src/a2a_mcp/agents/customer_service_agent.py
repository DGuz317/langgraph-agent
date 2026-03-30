import os
import logging
import uvicorn
import asyncio

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH

import httpx


logger = logging.getLogger(__name__)


langgraph_orchestrator = RemoteA2aAgent(
    name="OrchestratorAgent",
    description="Facilitate inter agent communication",
    agent_card=(
        f"http://localhost:8040/{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
    timeout=300.0,
) 

Customer_Service_Agent = Agent(
    name="Customer_Service_Agent",
    model="gemini-2.5-flash",
    description="Customer service agent for a digital music store",
    instruction="""
        You are the friendly frontend assistant for our digital music store. 
        If they ask about music tracks, albums, or their invoices, 
        you MUST use the 'Orchestrator Agent' to find the answer
        """,
    tools=[],
    sub_agents=[langgraph_orchestrator],
)

root_agent = Customer_Service_Agent
logger.info("Initializing adk agent...")

app = get_fast_api_app(
    agents_dir=os.path.abspath(os.path.dirname(r"C:\Users\nvdung1\Desktop\langraph_agent\src\a2a_mcp")),
    web=True,
    a2a=True
)

# print("\n" + "="*50)
# print("URL list (ENDPOINTS) created:")
# print("="*50)

# for route in app.routes:
#     if hasattr(route, "methods") and hasattr(route, "path"):
#         methods = ", ".join(route.methods)
#         print(f"[{methods:^10}] -> {route.path}")
#     elif hasattr(route, "path"):
#         print(f"[  MOUNTED  ] -> {route.path}")

# print("="*50 + "\n")
