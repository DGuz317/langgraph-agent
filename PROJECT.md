# Multi-Agent System Using LangGraph

## Overview
The goal of the project is to build a **multi-agent system** that consists of different agents communicating with each other. The system uses **LangGraph**, **A2A protocol**, and **MCP tools** to handle user queries related to invoices and music. The system provides a flexible architecture that can be expanded to other domains and agents in the future.

## Key Components:
### Agents:
#### Invoice Agent
- Retrieves and processes invoice information using MCP tools.
- Exposed via A2A service.
#### Music Agent
- Retrieves music-related information (tracks, albums, genres) via MCP tools.
- Exposed via A2A service.
#### Planner Agent
- Receives user input and generates tasks for specialized agents (Invoice and Music).
- Includes **Human-in-the-Loop (HITL)** to handle missing information.
- Orchestrates the flow between invoice and music agents.
#### Aggregator Agent
- Combines the results of multiple agents (Invoice + Music) into a final response.

## Architecture Overview
The system is designed with **separation of concerns** and modularity in mind:
- **MCP server**: Handles database queries for invoices and music data.
- **A2A services**: Exposes the Invoice and Music agents via A2A endpoints.
- **Planner**: The core decision-making engine that decides which agent to call based on the user's input.
- **Aggregator**: Aggregates the results from multiple agents into a single response.
- **LLM**: The Planner agent uses LLM to understand and process user queries.

## File Structure
```bash
multi-agent-system/
├── graphify-out
│   ├── graph.html
│   ├── graph.json
│   └── GRAPH_REPORT.md
├── langgraph.json
├── PROJECT.md
├── pyproject.toml
├── README.md
├── scripts
│   ├── run_invoice_a2a.py
│   ├── run_mcp_server.py
│   ├── run_music_a2a.py
│   └── run_planner.py
├── src
│   └── multi_agent_system
│       ├── a2a_client
│       │   ├── base.py
│       │   ├── __init__.py
│       │   ├── invoice_client.py
│       │   ├── music_client.py
│       │   └── schemas.py
│       ├── a2a_servers
│       │   ├── __init__.py
│       │   ├── invoice_agent
│       │   │   ├── agent.py
│       │   │   ├── executor.py
│       │   │   ├── __init__.py
│       │   │   ├── prompts.py
│       │   │   ├── schemas.py
│       │   │   └── server.py
│       │   └── music_agent
│       │       ├── agent.py
│       │       ├── executor.py
│       │       ├── __init__.py
│       │       ├── prompts.py
│       │       ├── schemas.py
│       │       └── server.py
│       ├── agent_cards
│       │   ├── invoice_agent.json
│       │   └── music_agent.json
│       ├── aggregator
│       │   ├── agent.py
│       │   ├── __init__.py
│       │   ├── prompts.py
│       │   └── schemas.py
│       ├── common
│       │   ├── agent_card_loader.py
│       │   ├── constants.py
│       │   ├── errors.py
│       │   ├── __init__.py
│       │   ├── llm.py
│       │   ├── mcp_tool_agent.py
│       │   └── types.py
│       ├── config.py
│       ├── __init__.py
│       ├── mcp_server
│       │   ├── chinook.db
│       │   ├── db.py
│       │   ├── __init__.py
│       │   ├── schemas.py
│       │   ├── server.py
│       │   └── tools
│       │       ├── __init__.py
│       │       ├── invoice_tools.py
│       │       └── music_tools.py
│       ├── planner
│       │   ├── agent.py
│       │   ├── __init__.py
│       │   ├── prompts.py
│       │   └── schemas.py
│       └── planner_app
│           ├── edges.py
│           ├── graph.py
│           ├── hitl.py
│           ├── __init__.py
│           ├── nodes.py
│           ├── schemas.py
|           ├── task_instructions.py
│           └── state.py
├── tests
│   ├── test_a2a_clients.py
|   ├── test_aggregator.py
│   ├── test_invoice_a2a_client.py
│   ├── test_llm_planner.py
│   ├── test_mcp_tools.py
│   ├── test_music_a2a_client.py
│   ├── test_planner_graph.py
|   ├── test_task_instructions.py
│   └── test_planner_hitl.py
└── uv.lock
```

## Configuration
### config.py

The `config.py` file loads configuration settings from `.env`and provides access to the configuration in a structured way using **Pydantic**.

```python
from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    model_provider: Literal["ollama", "openai", "google", "anthropic"] = "ollama"
    llm_model: str = "gpt-oss"
    llm_temperature: float = 0.0
    ollama_api_url: str = "http://localhost:11434"
    openai_api_key: str | None = None
    google_api_key: str | None = None
    anthropic_api_key: str | None = None
    sqlite_db: str
    mcp_server_url: str = "http://localhost:10000/mcp"
    invoice_a2a_url: str = "http://localhost:11001"
    music_a2a_url: str = "http://localhost:11002"
    a2a_timeout_seconds: int = 30
    langsmith_api_key: str = "lsv2_your_key_here"
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_tracing: bool = False
    langsmith_project: str = "multi-agent-system"
```
The `.env` file contains:
```python
MODEL_PROVIDER=ollama
LLM_MODEL=gpt-oss
LLM_TEMPERATURE=0
OLLAMA_API_URL=http://localhost:11434
SQLITE_DB=sqlite:////home/your_path/chinook.db
MCP_SERVER_URL=http://localhost:10000/mcp
INVOICE_A2A_URL=http://localhost:11001
MUSIC_A2A_URL=http://localhost:11002
A2A_TIMEOUT_SECONDS=30
```
The configuration is structured to support **Ollama**, **OpenAI**, **Google**, and **Anthropic** providers.
## MCP Server
The MCP server uses **SQLAlchemy** and **SQLDatabase** to query and return data related to invoices and music:
```python
from langchain_community.utilities import SQLDatabase
from multi_agent_system.config import settings

def get_db() -> SQLDatabase:
    return SQLDatabase.from_uri(settings.sqlite_db)
```
The server is launched using:
```bash
uv run python scripts/run_mcp_server.py --host localhost --port 10000 --transport streamable-http
```
## A2A Services
Each agent is exposed via A2A:

- **Invoice Agent**: Handles invoice-related tasks.
- **Music Agent**: Handles music-related tasks.

The A2A server for each agent is created using **FastAPI** and **A2A SDK v1**.

Example for Invoice Agent:
```python
import click
import uvicorn
from fastapi import FastAPI

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore

from multi_agent_system.common.agent_card_loader import load_agent_card
from multi_agent_system.a2a_servers.invoice_agent.executor import (
    InvoiceAgentExecutor,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Invoice A2A Service",
        version="1.0.0",
    )

    agent_card = load_agent_card("invoice_agent.json")

    request_handler = DefaultRequestHandler(
        agent_executor=InvoiceAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    for route in create_agent_card_routes(agent_card):
        app.router.routes.append(route)

    for route in create_jsonrpc_routes(
        request_handler,
        rpc_url="/a2a/jsonrpc/",
    ):
        app.router.routes.append(route)

    return app


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=11001)
def main(host: str, port: int) -> None:
    app = create_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
```
## Agent Cards
Agent cards are static JSON files stored in `src/multi_agent_system/agent_cards/`:

- **invoice_agent.json**
- **music_agent.json**

The agent card defines the supported interfaces, capabilities, and tasks that the agent can perform.

Example for **Invoice Agent**:
```json
{
  "name": "Invoice Agent",
  "supportedInterfaces": [
    {
      "protocolBinding": "JSONRPC",
      "url": "http://localhost:11001/a2a/jsonrpc/"
    }
  ],
  "capabilities": {
    "streaming": false,
    "pushNotifications": false
  },
  "skills": [
    {
      "id": "invoice_retrieval",
      "name": "Invoice information retrieval",
      "description": "Retrieve invoices by customer ID",
      "tags": ["invoice", "customer"]
    }
  ]
}
```
## A2A Clients
Reusable A2A clients are created for Invoice and Music agents:
```python
class InvoiceA2AClient(BaseA2AClient):
    def __init__(self) -> None:
        super().__init__(
            url=f"{settings.invoice_a2a_url.rstrip('/')}/a2a/jsonrpc/",
            timeout_seconds=settings.a2a_timeout_seconds,
        )

    async def get_latest_invoice(self, customer_id: str) -> str:
        return await self.ask(f"Get latest invoice for customer_id={customer_id}")
```

## Planner Graph
The planner graph is composed of nodes and edges that define the sequence of actions:
```python
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver

from multi_agent_system.planner_app.edges import (
    route_after_invoice,
    route_after_planner,
)
from multi_agent_system.planner_app.nodes import (
    final_response_node,
    invoice_node,
    missing_info_node,
    music_node,
    planner_node,
)
from multi_agent_system.planner_app.state import PlannerAppState


def build_graph():
    graph = StateGraph(PlannerAppState)

    graph.add_node("planner", planner_node)
    graph.add_node("missing_info", missing_info_node)
    graph.add_node("invoice", invoice_node)
    graph.add_node("music", music_node)
    graph.add_node("final_response", final_response_node)

    graph.add_edge(START, "planner")

    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "missing_info": "missing_info",
            "invoice": "invoice",
            "music": "music",
            "final_response": "final_response",
        },
    )

    graph.add_conditional_edges(
        "missing_info",
        route_after_planner,
        {
            "missing_info": "missing_info",
            "invoice": "invoice",
            "music": "music",
            "final_response": "final_response",
        },
    )

    graph.add_conditional_edges(
        "invoice",
        route_after_invoice,
        {
            "music": "music",
            "final_response": "final_response",
        },
    )

    graph.add_edge("music", "final_response")
    graph.add_edge("final_response", END)


    checkpointer = InMemorySaver()
    return graph.compile(checkpointer=checkpointer)


planner_graph = build_graph()
```

## HITL and Aggregator
The **HITL (Human-In-The-Loop)** functionality is implemented using LangGraph’s interrupt method. If information is missing, the graph interrupts and asks the user for more details before proceeding.

The **Aggregator** is responsible for combining results from both agents (Invoice and Music) and presenting a final answer:
```python
import json

from multi_agent_system.aggregator.schemas import (
    AgentResult,
    AggregatorInput,
    AggregatorOutput,
)


class AggregatorAgent:
    def invoke(self, data: AggregatorInput) -> AggregatorOutput:
        sections: list[str] = []

        for result in data.results:
            parsed = self._try_parse_json(result.result)

            if parsed:
                sections.append(
                    self._format_structured_result(
                        agent=result.agent,
                        data=parsed,
                    )
                )
            else:
                sections.append(
                    f"{result.agent.title()} result:\n{result.result}"
                )

        return AggregatorOutput(
            final_answer="\n\n".join(sections)
        )

    def _try_parse_json(self, text: str) -> dict | None:
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return None

        return parsed if isinstance(parsed, dict) else None

    def _format_structured_result(self, agent: str, data: dict) -> str:
        success = data.get("success")
        content = data.get("content")
        payload = data.get("data")

        title = f"{agent.title()} result"

        if success is False:
            return f"{title}:\nFailed: {content}"

        if payload is None:
            return f"{title}:\n{content}"

        formatted_payload = json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )

        return f"{title}:\n{content}\n\nData:\n{formatted_payload}"
```

## Future Improvements
- Replace **deterministic planner** with **LLM-powered planner** that can handle more complex user queries.
- Expand **Aggregator** to support more flexible result composition (e.g., file generation, advanced data formatting).
- Add **multi-agent parallel execution** for better performance in complex workflows.

## Run Commands
To run the system, use the following commands:

**1. Start MCP server:**
```bash
uv run python scripts/run_mcp_server.py --host localhost --port 10000 --transport streamable-http
```
**2. Start Invoice A2A service:**
```bash
uv run python scripts/run_invoice_a2a.py --host localhost --port 11001
```
**3. Start Music A2A service:**
```bash
uv run python scripts/run_music_a2a.py --host localhost --port 11002
```
**4. Run Planner graph test:**
```bash
uv run python tests/test_planner_graph.py
```
**5. Run LLM Planner test:**
```bash
uv run python tests/test_llm_planner.py
```
**6. Run the planner CLI:**
```bash
uv run python scripts/run_planner.py
```
This markdown summarizes the entire project flow, from setup and architecture to agent-specific configurations and the final LLM-based improvements.













