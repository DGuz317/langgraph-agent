# langgraph-agent
## Requirements
- Python
- uv
## Project Structure
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
│           └── state.py
├── tests
│   ├── test_a2a_clients.py
│   ├── test_invoice_a2a_client.py
│   ├── test_llm_planner.py
│   ├── test_mcp_tools.py
│   ├── test_music_a2a_client.py
│   ├── test_planner_graph.py
│   └── test_planner_hitl.py
└── uv.lock
```
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
**4. Run Pytest:**
```bash
uv run pytest tests -q
RUN_A2A_INTEGRATION_TESTS=1 uv run pytest tests/test_invoice_a2a_client.py tests/test_music_a2a_client.py -q
RUN_MCP_INTEGRATION_TESTS=1 uv run pytest tests/test_mcp_tools.py -q
RUN_LLM_TESTS=1 uv run pytest tests/test_llm_planner.py -q
```
**6. Run the planner integartion CLI:**
```bash
uv run python scripts/run_planner.py
```