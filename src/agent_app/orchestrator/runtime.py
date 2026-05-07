import os
import asyncio
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from agent_app.agents.invoice_agent import build_invoice_agent
from agent_app.agents.music_agent import build_music_agent
from agent_app.agents.planner_agent import build_planner_agent
from agent_app.agents.aggregator_agent import build_aggregator_agent

from agent_app.orchestrator.graph import build_graph


load_dotenv()

class AgentRuntime:
    def __init__(self):
        self.client = None
        self._session_cm = None
        self.session = None
        self.agents = {}
        self.graph = None

    async def start(self):
        # --- Model ---
        model = init_chat_model(
            model=os.getenv("LLM_MODEL"),
            model_provider=os.getenv("MODEL_PROVIDER"),
            base_url=os.getenv("OLLAMA_API_URL"),
            temperature=0,
            timeout=300,
            max_tokens=25000,
        )

        checkpointer = InMemorySaver()

        # --- MCP client ---
        self.client = MultiServerMCPClient({
            "data_tools": {
                "transport": "streamable-http",
                "url": "http://localhost:10000/mcp"
            }
        })

        self._session_cm = self.client.session("data_tools")
        self.session = await self._session_cm.__aenter__()

        # --- Build agents ---
        invoice_agent = await build_invoice_agent(self.session, model, checkpointer)
        music_agent = await build_music_agent(self.session, model, checkpointer)
        planner_agent = build_planner_agent(model, checkpointer)
        aggregator_agent = build_aggregator_agent(model, checkpointer)

        self.agents = {
            "invoice_agent": invoice_agent,
            "music_agent": music_agent,
            "planner": planner_agent,
            "aggregator": aggregator_agent,
        }

        self.graph = build_graph(self.agents)
        return self.agents, self.graph

    async def stop(self):
        if self._session_cm:
            await self._session_cm.__aexit__(None, None, None)
