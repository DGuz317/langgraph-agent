# Multi-Agent System with LangGraph, A2A, and MCP

A Python multi-agent system that routes user requests to specialized agents for invoice and music data. The project uses **LangGraph** for orchestration, **A2A** for agent-to-agent communication, **FastMCP** for database-backed tools, and the Chinook SQLite database as the sample data source.

## Current Capabilities

The system can:

- Get the latest invoice for a customer.
- Get a customer's invoices sorted by invoice line unit price.
- Find tracks by artist.
- Find albums by artist.
- Recommend songs by genre.
- Check whether a song exists by title.
- Ask the user for missing information through LangGraph human-in-the-loop interrupts.
- Combine one or more agent results into a single final answer.

## Architecture

```text
User query
  ↓
Planner LangGraph App
  ↓
LLM Planner Agent
  ↓
Missing required fields?
  ├── Yes → HITL interrupt → user reply → resume graph
  └── No
       ↓
       Task routing
       ├── Invoice A2A Client → Invoice A2A Service → Invoice MCP tools → Chinook DB
       └── Music A2A Client   → Music A2A Service   → Music MCP tools   → Chinook DB
       ↓
Aggregator Agent
  ↓
Final answer
```

## Design Principles

- **Planner owns intent detection.** It converts user input into structured tasks.
- **HITL owns missing information collection.** It resumes the same graph thread after the user replies.
- **Task args are the source of truth.** `task["args"]` should drive execution.
- **Instruction strings are compatibility output.** Instructions are generated from `intent + args` before calling the current text-based A2A services.
- **Domain agents stay focused.** Invoice and music agents parse clean instructions, call MCP tools, and return structured responses.
- **MCP tools only access data.** They should not own planning, routing, HITL, or aggregation logic.
- **Aggregator formats results.** It combines one or more agent outputs into the final user-facing response.

## Core Components

| Component | Responsibility |
|---|---|
| `planner/` | LLM planner, task schemas, planner prompt |
| `planner_app/` | LangGraph workflow, nodes, edges, HITL, task execution |
| `a2a_servers/invoice_agent/` | Invoice A2A service and invoice domain agent |
| `a2a_servers/music_agent/` | Music A2A service and music domain agent |
| `a2a_client/` | Reusable JSON-RPC A2A clients |
| `mcp_server/` | FastMCP server, SQLite access, invoice/music tools |
| `aggregator/` | Final response formatting and result composition |
| `common/` | Shared config, LLM setup, MCP tool agent base, utilities |
| `agent_cards/` | Static A2A agent card JSON files |
| `tests/` | Unit, parser, planner, MCP, A2A, and integration tests |

## Project Structure

```text
multi-agent-system/
├── README.md
├── PROJECT.md
├── pyproject.toml
├── uv.lock
├── langgraph.json
├── scripts/
│   ├── run_mcp_server.py
│   ├── run_invoice_a2a.py
│   ├── run_music_a2a.py
│   └── run_planner.py
├── src/
│   └── multi_agent_system/
│       ├── __init__.py
│       ├── config.py
│       ├── common/
│       │   ├── agent_card_loader.py
│       │   ├── constants.py
│       │   ├── errors.py
│       │   ├── llm.py
│       │   ├── mcp_tool_agent.py
│       │   └── types.py
│       ├── agent_cards/
│       │   ├── invoice_agent.json
│       │   └── music_agent.json
│       ├── mcp_server/
│       │   ├── chinook.db
│       │   ├── db.py
│       │   ├── schemas.py
│       │   ├── server.py
│       │   └── tools/
│       │       ├── invoice_tools.py
│       │       └── music_tools.py
│       ├── a2a_servers/
│       │   ├── invoice_agent/
│       │   │   ├── agent.py
│       │   │   ├── executor.py
│       │   │   ├── prompts.py
│       │   │   ├── schemas.py
│       │   │   └── server.py
│       │   └── music_agent/
│       │       ├── agent.py
│       │       ├── executor.py
│       │       ├── prompts.py
│       │       ├── schemas.py
│       │       └── server.py
│       ├── a2a_client/
│       │   ├── base.py
│       │   ├── invoice_client.py
│       │   ├── music_client.py
│       │   └── schemas.py
│       ├── planner/
│       │   ├── agent.py
│       │   ├── prompts.py
│       │   └── schemas.py
│       ├── planner_app/
│       │   ├── edges.py
│       │   ├── graph.py
│       │   ├── hitl.py
│       │   ├── nodes.py
│       │   ├── schemas.py
│       │   ├── state.py
│       │   └── task_instructions.py
│       └── aggregator/
│           ├── agent.py
│           ├── prompts.py
│           └── schemas.py
└── tests/
    ├── test_aggregator.py
    ├── test_a2a_clients.py
    ├── test_invoice_agent_parsing.py
    ├── test_invoice_a2a_client.py
    ├── test_llm_planner.py
    ├── test_mcp_tools.py
    ├── test_music_agent_parsing.py
    ├── test_music_a2a_client.py
    ├── test_planner_graph.py
    ├── test_planner_hitl.py
    └── test_task_instructions.py
```

## Requirements

- Python 3.12+
- `uv`
- Ollama, OpenAI, Google Gemini, or Anthropic as the LLM provider
- SQLite Chinook database included in the project

## Setup

Install dependencies:

```bash
uv sync
```

Create a local `.env` file:

```env
MODEL_PROVIDER=ollama
LLM_MODEL=gpt-oss
LLM_TEMPERATURE=0
OLLAMA_API_URL=http://localhost:11434

OPENAI_API_KEY=
GOOGLE_API_KEY=
ANTHROPIC_API_KEY=

SQLITE_DB=sqlite:////absolute/path/to/src/multi_agent_system/mcp_server/chinook.db

MCP_SERVER_URL=http://localhost:10000/mcp
INVOICE_A2A_URL=http://localhost:11001
MUSIC_A2A_URL=http://localhost:11002
A2A_TIMEOUT_SECONDS=30

LANGSMITH_API_KEY=
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_TRACING=false
LANGSMITH_PROJECT=multi-agent-system
```

Security notes:

- Do not hardcode API keys inside `config.py`.
- Keep `.env` out of Git.
- Commit `.env.example`, not `.env`.

## Running the System

Start each service in a separate terminal.

### 1. Start MCP server

```bash
uv run python scripts/run_mcp_server.py --host localhost --port 10000 --transport streamable-http
```

### 2. Start Invoice A2A service

```bash
uv run python scripts/run_invoice_a2a.py --host localhost --port 11001
```

### 3. Start Music A2A service

```bash
uv run python scripts/run_music_a2a.py --host localhost --port 11002
```

### 4. Run Planner CLI

```bash
uv run python scripts/run_planner.py
```

## Example Prompts

Direct invoice queries:

```text
Get latest invoice for customer_id=5
Show invoices for customer_id=5 sorted by unit price
```

Direct music queries:

```text
Find tracks by artist AC/DC
Find albums by artist Accept
Recommend songs by genre rock
Check for song Ligia
Check for song Let There Be Rock
song_title=Desafinado
```

HITL examples:

```text
User: What is my latest invoice?
Assistant: Could you provide your customer ID?
User: 5
```

```text
User: Recommend some songs
Assistant: Do you want to search by artist or by genre?
User: Jazz
```

```text
User: Recommend some songs
Assistant: Do you want to search by artist or by genre?
User: artist AC/DC
```

Multi-agent query:

```text
Get latest invoice for customer_id=5 and find tracks by artist AC/DC
```

## Testing

Run all local tests:

```bash
uv run pytest tests -q
```

Run focused unit tests:

```bash
uv run pytest tests/test_aggregator.py -q
uv run pytest tests/test_task_instructions.py -q
uv run pytest tests/test_invoice_agent_parsing.py -q
uv run pytest tests/test_music_agent_parsing.py -q
uv run pytest tests/test_planner_graph.py -q
uv run pytest tests/test_planner_hitl.py -q
```

Run LLM planner tests:

```bash
RUN_LLM_TESTS=1 uv run pytest tests/test_llm_planner.py -q
```

Run MCP integration tests:

```bash
RUN_MCP_INTEGRATION_TESTS=1 uv run pytest tests/test_mcp_tools.py -q
```

Run A2A integration tests after starting the MCP server and both A2A services:

```bash
RUN_A2A_INTEGRATION_TESTS=1 uv run pytest tests/test_invoice_a2a_client.py tests/test_music_a2a_client.py -q
```

## Development Workflow

Recommended workflow before adding features:

```bash
uv run pytest tests -q
git status
git commit -m "Stabilize multi-agent planner execution"
```

Recommended flow for new changes:

```text
1. Add or update schema.
2. Add unit tests.
3. Implement the smallest code change.
4. Run focused tests.
5. Run full local tests.
6. Run integration tests if A2A or MCP behavior changed.
7. Update README.md and PROJECT.md.
```

### A2A integration test fails with connection error

Start all required services first:

```bash
uv run python scripts/run_mcp_server.py --host localhost --port 10000 --transport streamable-http
uv run python scripts/run_invoice_a2a.py --host localhost --port 11001
uv run python scripts/run_music_a2a.py --host localhost --port 11002
```

## Knowledge Graph

This repository can include Graphify output under:

```text
graphify-out/
├── GRAPH_REPORT.md
├── graph.html
└── graph.json
```

After code changes, refresh the graph if Graphify is installed:

```bash
graphify update .
```

## Roadmap

Recommended next improvements:

- Add planner end-to-end tests for full user flows.
- Improve graph-node error recovery for unavailable A2A/MCP services.
- Parameterize all SQL queries.
- Add persistent checkpointer for production usage.
- Add structured A2A payload support so agents no longer need text instruction parsing.
- Add parallel task execution after the sequential path is stable.
- Add deployment documentation for remote A2A service discovery.

## Current Status

The current version is a sequential, debuggable multi-agent workflow. It is designed for correctness first:

```text
Planner → optional HITL → invoice/music task execution → aggregation → final answer
```

Parallel execution and broader agent capabilities should be added only after the current sequential graph is covered by end-to-end tests.