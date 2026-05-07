# Graph Report - .  (2026-05-07)

## Corpus Check
- Corpus is ~6,185 words - fits in a single context window. You may not need a graph.

## Summary
- 169 nodes · 111 edges · 54 communities detected
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 23 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_MCP Server server.py|MCP Server: server.py]]
- [[_COMMUNITY_Planner Agent build_aggregator_agent()|Planner Agent: build_aggregator_agent()]]
- [[_COMMUNITY_Orchestrator graph.py|Orchestrator: graph.py]]
- [[_COMMUNITY_Orchestrator runtime.py|Orchestrator: runtime.py]]
- [[_COMMUNITY_Invoice Agent agent.py|Invoice Agent: agent.py]]
- [[_COMMUNITY_Music Agent agent.py|Music Agent: agent.py]]
- [[_COMMUNITY_README Customer ID 2|README: Customer ID 2]]
- [[_COMMUNITY_README ACDC|README: AC/DC]]
- [[_COMMUNITY_Tests conftest.py|Tests: conftest.py]]
- [[_COMMUNITY_Refund Agent process_refund()|Refund Agent: process_refund()]]
- [[_COMMUNITY_Database get_engine_for_chinook_db|Database: get_engine_for_chinook_db]]
- [[_COMMUNITY_README langgraph-agent|README: langgraph-agent]]
- [[_COMMUNITY_Invoice Agent test_invoice.py|Invoice Agent: test_invoice.py]]
- [[_COMMUNITY_Planner Agent test_planner.py|Planner Agent: test_planner.py]]
- [[_COMMUNITY_Music Agent test_music.py|Music Agent: test_music.py]]
- [[_COMMUNITY_README planner_agent_2.py|README: planner_agent_2.py]]
- [[_COMMUNITY_README refund_agent.json|README: refund_agent.json]]
- [[_COMMUNITY_README orchestrator_agent.json|README: orchestrator_agent.json]]
- [[_COMMUNITY_README adk web|README: adk web]]
- [[_COMMUNITY_README assets|README: assets/]]
- [[_COMMUNITY_README MultiAgentSystem.png|README: MultiAgentSystem.png]]
- [[_COMMUNITY_README graphify-out|README: graphify-out/]]
- [[_COMMUNITY_README graph.html|README: graph.html]]
- [[_COMMUNITY_README graph.json|README: graph.json]]
- [[_COMMUNITY_README GRAPH_REPORT|README: GRAPH_REPORT]]
- [[_COMMUNITY_README memory|README: memory/]]
- [[_COMMUNITY_README pyproject.toml|README: pyproject.toml]]
- [[_COMMUNITY_README run.sh|README: run.sh]]
- [[_COMMUNITY_README srcagent_app|README: src/agent_app/]]
- [[_COMMUNITY_README agent_cards|README: agent_cards/]]
- [[_COMMUNITY_README agents|README: agents/]]
- [[_COMMUNITY_README agents__init__|README: agents/__init__]]
- [[_COMMUNITY_README agents__main__|README: agents/__main__]]
- [[_COMMUNITY_README common|README: common/]]
- [[_COMMUNITY_README agent_executor.py|README: agent_executor.py]]
- [[_COMMUNITY_README base_agent.py|README: base_agent.py]]
- [[_COMMUNITY_README common__init__|README: common/__init__]]
- [[_COMMUNITY_README prompts.py|README: prompts.py]]
- [[_COMMUNITY_README types.py|README: types.py]]
- [[_COMMUNITY_README utils.py|README: utils.py]]
- [[_COMMUNITY_README workflow.py|README: workflow.py]]
- [[_COMMUNITY_README database|README: database/]]
- [[_COMMUNITY_README chinook.db|README: chinook.db]]
- [[_COMMUNITY_README get_database.py|README: get_database.py]]
- [[_COMMUNITY_README database__init__|README: database/__init__]]
- [[_COMMUNITY_README __init__.py|README: __init__.py]]
- [[_COMMUNITY_README mcp_server|README: mcp_server/]]
- [[_COMMUNITY_README mcp_server__init__|README: mcp_server/__init__]]
- [[_COMMUNITY_README server.py|README: server.py]]
- [[_COMMUNITY_README test|README: test/]]
- [[_COMMUNITY_README test_client.py|README: test_client.py]]
- [[_COMMUNITY_README test_orchestrator.py|README: test_orchestrator.py]]
- [[_COMMUNITY_README test_refund.py|README: test_refund.py]]
- [[_COMMUNITY_README uv.lock|README: uv.lock]]

## God Nodes (most connected - your core abstractions)
1. `AgentRuntime` - 7 edges
2. `main()` - 6 edges
3. `runtime()` - 4 edges
4. `build_graph()` - 4 edges
5. `ResponseFormat` - 4 edges
6. `ResponseFormat` - 4 edges
7. `ResponseFormat` - 4 edges
8. `test_full_pipeline()` - 3 edges
9. `test_orchestrator()` - 3 edges
10. `OrchestratorState` - 3 edges

## Surprising Connections (you probably didn't know these)
- `runtime()` --calls--> `AgentRuntime`  [INFERRED]
  test/conftest.py → src/agent_app/orchestrator/runtime.py
- `test_full_pipeline()` --calls--> `build_graph()`  [INFERRED]
  test/test_orchestrator.py → src/agent_app/orchestrator/graph.py
- `main()` --calls--> `AgentRuntime`  [INFERRED]
  src/main.py → src/agent_app/orchestrator/runtime.py

## Hyperedges (group relationships)
- **Agent Card JSONs** — README_invoice_agent_json, README_music_agent_json, README_orchestrator_agent_json, README_planner_agent_json, README_refund_agent_json [INFERRED 0.80]

## Communities

### Community 0 - "MCP Server: server.py"
Cohesion: 0.17
Nodes (15): check_for_songs(), get_albums_by_artist(), get_employee_by_invoice_and_customer(), get_invoices_by_customer_sorted_by_date(), get_invoices_sorted_by_unit_price(), get_songs_by_genre(), get_tracks_by_artist(), main() (+7 more)

### Community 1 - "Planner Agent: build_aggregator_agent()"
Cohesion: 0.25
Nodes (7): build_aggregator_agent(), ResponseFormat, BaseModel, build_planner_agent(), Structured plan produced by the planner agent., ResponseFormat, Task

### Community 2 - "Orchestrator: graph.py"
Cohesion: 0.24
Nodes (5): build_graph(), extract_structured(), OrchestratorState, test_full_pipeline(), TypedDict

### Community 3 - "Orchestrator: runtime.py"
Cohesion: 0.31
Nodes (3): AgentRuntime, main(), test_orchestrator()

### Community 4 - "Invoice Agent: agent.py"
Cohesion: 0.5
Nodes (3): build_invoice_agent(), Response to user using this format, ResponseFormat

### Community 5 - "Music Agent: agent.py"
Cohesion: 0.5
Nodes (3): build_music_agent(), Response to user using this format, ResponseFormat

### Community 6 - "README: Customer ID 2"
Cohesion: 0.4
Nodes (5): Customer ID 2, Customer ID 3, invoice_agent_2.py, invoice_agent.json, invoice_agent.py

### Community 7 - "README: AC/DC"
Cohesion: 0.4
Nodes (5): AC/DC, music_agent_2.py, music_agent.json, music_agent.py, Rolling Stones

### Community 8 - "Tests: conftest.py"
Cohesion: 0.67
Nodes (2): agents(), runtime()

### Community 9 - "Refund Agent: process_refund()"
Cohesion: 0.5
Nodes (2): process_refund(), Processes a refund for a customer. This is a sensitive action!

### Community 10 - "Database: get_engine_for_chinook_db"
Cohesion: 0.5
Nodes (2): get_engine_for_chinook_db(), Pull SQL file, populate in-memory database, and create engine.          Download

### Community 11 - "README: langgraph-agent"
Cohesion: 0.5
Nodes (4): langgraph-agent, Python, start_system.ps1, uv

### Community 12 - "Invoice Agent: test_invoice.py"
Cohesion: 0.67
Nodes (1): test_invoice_agent_single()

### Community 13 - "Planner Agent: test_planner.py"
Cohesion: 0.67
Nodes (1): test_planner_single_intent()

### Community 14 - "Music Agent: test_music.py"
Cohesion: 0.67
Nodes (1): test_music_agent_single()

### Community 15 - "README: planner_agent_2.py"
Cohesion: 0.67
Nodes (3): planner_agent_2.py, planner_agent.json, planner_agent.py

### Community 16 - "README: refund_agent.json"
Cohesion: 1.0
Nodes (2): refund_agent.json, refund_agent.py

### Community 17 - "README: orchestrator_agent.json"
Cohesion: 1.0
Nodes (2): orchestrator_agent.json, orchestrator_agent.py

### Community 18 - "README: adk web"
Cohesion: 1.0
Nodes (2): adk web, http://127.0.0.1:8050

### Community 51 - "README: assets/"
Cohesion: 1.0
Nodes (1): assets/

### Community 52 - "README: MultiAgentSystem.png"
Cohesion: 1.0
Nodes (1): MultiAgentSystem.png

### Community 53 - "README: graphify-out/"
Cohesion: 1.0
Nodes (1): graphify-out/

### Community 54 - "README: graph.html"
Cohesion: 1.0
Nodes (1): graphify-out/graph.html

### Community 55 - "README: graph.json"
Cohesion: 1.0
Nodes (1): graphify-out/graph.json

### Community 56 - "README: GRAPH_REPORT"
Cohesion: 1.0
Nodes (1): graphify-out/GRAPH_REPORT.md

### Community 57 - "README: memory/"
Cohesion: 1.0
Nodes (1): graphify-out/memory/

### Community 58 - "README: pyproject.toml"
Cohesion: 1.0
Nodes (1): pyproject.toml

### Community 60 - "README: run.sh"
Cohesion: 1.0
Nodes (1): run.sh

### Community 61 - "README: src/agent_app/"
Cohesion: 1.0
Nodes (1): src/agent_app/

### Community 62 - "README: agent_cards/"
Cohesion: 1.0
Nodes (1): src/agent_app/agent_cards/

### Community 63 - "README: agents/"
Cohesion: 1.0
Nodes (1): src/agent_app/agents/

### Community 64 - "README: agents/__init__"
Cohesion: 1.0
Nodes (1): src/agent_app/agents/__init__.py

### Community 65 - "README: agents/__main__"
Cohesion: 1.0
Nodes (1): src/agent_app/agents/__main__.py

### Community 66 - "README: common/"
Cohesion: 1.0
Nodes (1): src/agent_app/common/

### Community 67 - "README: agent_executor.py"
Cohesion: 1.0
Nodes (1): agent_executor.py

### Community 68 - "README: base_agent.py"
Cohesion: 1.0
Nodes (1): base_agent.py

### Community 69 - "README: common/__init__"
Cohesion: 1.0
Nodes (1): src/agent_app/common/__init__.py

### Community 70 - "README: prompts.py"
Cohesion: 1.0
Nodes (1): prompts.py

### Community 71 - "README: types.py"
Cohesion: 1.0
Nodes (1): types.py

### Community 72 - "README: utils.py"
Cohesion: 1.0
Nodes (1): utils.py

### Community 73 - "README: workflow.py"
Cohesion: 1.0
Nodes (1): workflow.py

### Community 74 - "README: database/"
Cohesion: 1.0
Nodes (1): src/agent_app/database/

### Community 75 - "README: chinook.db"
Cohesion: 1.0
Nodes (1): chinook.db

### Community 76 - "README: get_database.py"
Cohesion: 1.0
Nodes (1): get_database.py

### Community 77 - "README: database/__init__"
Cohesion: 1.0
Nodes (1): src/agent_app/database/__init__.py

### Community 78 - "README: __init__.py"
Cohesion: 1.0
Nodes (1): src/agent_app/__init__.py

### Community 79 - "README: mcp_server/"
Cohesion: 1.0
Nodes (1): src/agent_app/mcp_server/

### Community 80 - "README: mcp_server/__init__"
Cohesion: 1.0
Nodes (1): src/agent_app/mcp_server/__init__.py

### Community 81 - "README: server.py"
Cohesion: 1.0
Nodes (1): server.py

### Community 82 - "README: test/"
Cohesion: 1.0
Nodes (1): test/

### Community 83 - "README: test_client.py"
Cohesion: 1.0
Nodes (1): test_client.py

### Community 84 - "README: test_orchestrator.py"
Cohesion: 1.0
Nodes (1): test_orchestrator.py

### Community 85 - "README: test_refund.py"
Cohesion: 1.0
Nodes (1): test_refund.py

### Community 86 - "README: uv.lock"
Cohesion: 1.0
Nodes (1): uv.lock

## Knowledge Gaps
- **64 isolated node(s):** `Processes a refund for a customer. This is a sensitive action!`, `Structured plan produced by the planner agent.`, `Response to user using this format`, `Response to user using this format`, `Pull SQL file, populate in-memory database, and create engine.          Download` (+59 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Tests: conftest.py`** (4 nodes): `conftest.py`, `agents()`, `conftest.py`, `runtime()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Refund Agent: process_refund()`** (4 nodes): `process_refund()`, `Processes a refund for a customer. This is a sensitive action!`, `refund_agent.py`, `refund_agent.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Database: get_engine_for_chinook_db`** (4 nodes): `get_engine_for_chinook_db()`, `Pull SQL file, populate in-memory database, and create engine.          Download`, `get_database.py`, `get_database.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Invoice Agent: test_invoice.py`** (3 nodes): `test_invoice.py`, `test_invoice.py`, `test_invoice_agent_single()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Planner Agent: test_planner.py`** (3 nodes): `test_planner.py`, `test_planner.py`, `test_planner_single_intent()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Music Agent: test_music.py`** (3 nodes): `test_music.py`, `test_music.py`, `test_music_agent_single()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: refund_agent.json`** (2 nodes): `refund_agent.json`, `refund_agent.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: orchestrator_agent.json`** (2 nodes): `orchestrator_agent.json`, `orchestrator_agent.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: adk web`** (2 nodes): `adk web`, `http://127.0.0.1:8050`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: assets/`** (1 nodes): `assets/`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: MultiAgentSystem.png`** (1 nodes): `MultiAgentSystem.png`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: graphify-out/`** (1 nodes): `graphify-out/`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: graph.html`** (1 nodes): `graphify-out/graph.html`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: graph.json`** (1 nodes): `graphify-out/graph.json`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: GRAPH_REPORT`** (1 nodes): `graphify-out/GRAPH_REPORT.md`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: memory/`** (1 nodes): `graphify-out/memory/`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: pyproject.toml`** (1 nodes): `pyproject.toml`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: run.sh`** (1 nodes): `run.sh`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: src/agent_app/`** (1 nodes): `src/agent_app/`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: agent_cards/`** (1 nodes): `src/agent_app/agent_cards/`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: agents/`** (1 nodes): `src/agent_app/agents/`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: agents/__init__`** (1 nodes): `src/agent_app/agents/__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: agents/__main__`** (1 nodes): `src/agent_app/agents/__main__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: common/`** (1 nodes): `src/agent_app/common/`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: agent_executor.py`** (1 nodes): `agent_executor.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: base_agent.py`** (1 nodes): `base_agent.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: common/__init__`** (1 nodes): `src/agent_app/common/__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: prompts.py`** (1 nodes): `prompts.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: types.py`** (1 nodes): `types.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: utils.py`** (1 nodes): `utils.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: workflow.py`** (1 nodes): `workflow.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: database/`** (1 nodes): `src/agent_app/database/`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: chinook.db`** (1 nodes): `chinook.db`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: get_database.py`** (1 nodes): `get_database.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: database/__init__`** (1 nodes): `src/agent_app/database/__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: __init__.py`** (1 nodes): `src/agent_app/__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: mcp_server/`** (1 nodes): `src/agent_app/mcp_server/`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: mcp_server/__init__`** (1 nodes): `src/agent_app/mcp_server/__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: server.py`** (1 nodes): `server.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: test/`** (1 nodes): `test/`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: test_client.py`** (1 nodes): `test_client.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: test_orchestrator.py`** (1 nodes): `test_orchestrator.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: test_refund.py`** (1 nodes): `test_refund.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README: uv.lock`** (1 nodes): `uv.lock`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AgentRuntime` connect `Orchestrator: runtime.py` to `Tests: conftest.py`, `Orchestrator: graph.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `build_planner_agent()` connect `Planner Agent: build_aggregator_agent()` to `Orchestrator: graph.py`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `AgentRuntime` (e.g. with `runtime()` and `main()`) actually correct?**
  _`AgentRuntime` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `main()` (e.g. with `AgentRuntime` and `.start()`) actually correct?**
  _`main()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `runtime()` (e.g. with `AgentRuntime` and `.start()`) actually correct?**
  _`runtime()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `build_graph()` (e.g. with `test_full_pipeline()` and `.start()`) actually correct?**
  _`build_graph()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Processes a refund for a customer. This is a sensitive action!`, `Structured plan produced by the planner agent.`, `Response to user using this format` to the rest of the system?**
  _64 weakly-connected nodes found - possible documentation gaps or missing edges._