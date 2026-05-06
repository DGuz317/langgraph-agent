# Graph Report - .  (2026-05-06)

## Corpus Check
- Corpus is ~7,527 words - fits in a single context window. You may not need a graph.

## Summary
- 192 nodes · 256 edges · 14 communities detected
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 28 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Invoice Agent|Invoice Agent]]
- [[_COMMUNITY_Workflow Core|Workflow Core]]
- [[_COMMUNITY_MCP Server Tools|MCP Server Tools]]
- [[_COMMUNITY_Agent Executor|Agent Executor]]
- [[_COMMUNITY_Workflow Status|Workflow Status]]
- [[_COMMUNITY_Main Entry Point|Main Entry Point]]
- [[_COMMUNITY_Common Types & Utils|Common Types & Utils]]
- [[_COMMUNITY_A2A Server & Agents|A2A Server & Agents]]
- [[_COMMUNITY_Orchestrator V2|Orchestrator V2]]
- [[_COMMUNITY_Orchestrator V1 (Legacy)|Orchestrator V1 (Legacy)]]
- [[_COMMUNITY_Music Agent|Music Agent]]
- [[_COMMUNITY_Test Orchestrator|Test Orchestrator]]
- [[_COMMUNITY_Refund Agent|Refund Agent]]
- [[_COMMUNITY_Database Layer|Database Layer]]

## God Nodes (most connected - your core abstractions)
1. `GenericAgentExecutor` - 12 edges
2. `WorkflowGraph` - 10 edges
3. `ServerConfig` - 10 edges
4. `main()` - 9 edges
5. `main()` - 9 edges
6. `Orchestrator Agent` - 8 edges
7. `WorkflowNode` - 7 edges
8. `BaseAgent` - 7 edges
9. `init_session()` - 6 edges
10. `get_mcp_server_config()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `GenericAgentExecutor`  [INFERRED]
  agents/main.py → src/agent_app/common/agent_executor.py
- `Get the agent, given an agent card.` --uses--> `GenericAgentExecutor`  [INFERRED]
  src/agent_app/agents/__main__.py → src/agent_app/common/agent_executor.py
- `Starts an Agent server.` --uses--> `GenericAgentExecutor`  [INFERRED]
  src/agent_app/agents/__main__.py → src/agent_app/common/agent_executor.py
- `Starts an Agent server.` --rationale_for--> `main()`  [EXTRACTED]
  src/agent_app/agents/__main__.py → agents/main.py
- `Response to user using this format` --rationale_for--> `ResponseFormat`  [EXTRACTED]
  src/agent_app/agents/invoice_agent.py → agents/invoice_agent.py

## Hyperedges (group relationships)
- **Service Agents Exposed by A2A** — multiagentsystem_refund_agent, multiagentsystem_music_agent, multiagentsystem_invoice_agent [EXTRACTED 0.97]

## Communities

### Community 0 - "Invoice Agent"
Cohesion: 0.09
Nodes (20): init_invoice_agent(), invoice_agent_response(), Response to user using this format, Response to user using this format, ResponseFormat, Initialize all agents in order.     MCP server must already be running before th, startup(), init_planner_agent() (+12 more)

### Community 1 - "Workflow Core"
Cohesion: 0.15
Nodes (18): Represents a single node in a workflow graph.      Each node encapsulates a spec, WorkflowNode, cli(), find_agent(), find_resource(), get_invoices_by_customer_sorted_by_date(), get_tracks_by_artist(), init_session() (+10 more)

### Community 2 - "MCP Server Tools"
Cohesion: 0.17
Nodes (15): check_for_songs(), get_albums_by_artist(), get_employee_by_invoice_and_customer(), get_invoices_by_customer_sorted_by_date(), get_invoices_sorted_by_unit_price(), get_songs_by_genre(), get_tracks_by_artist(), main() (+7 more)

### Community 3 - "Agent Executor"
Cohesion: 0.19
Nodes (6): ABC, AgentExecutor, GenericAgentExecutor, AgentExecutor used by invoice agents and music agent, BaseAgent, Base class for agents.

### Community 4 - "Workflow Status"
Cohesion: 0.19
Nodes (5): Represents a graph of workflow nodes., Represents the status of a workflow and its associated node., Status, WorkflowGraph, Enum

### Community 5 - "Main Entry Point"
Cohesion: 0.21
Nodes (11): get_agent(), main(), Get the agent, given an agent card., Music query — single task, no aggregation needed., Starts an Agent server., Both music and invoice — two tasks, aggregation needed., Invoice query with no customer ID.     Turn 1 → ask_user returns clarification., test_missing_info() (+3 more)

### Community 6 - "Common Types & Utils"
Cohesion: 0.27
Nodes (11): Server Confgiguration., ServerConfig, config_logger(), config_logging(), get_mcp_server_config(), init_api_key(), Initialize the API key for Google Generative AI., Configure basic logging. (+3 more)

### Community 7 - "A2A Server & Agents"
Cohesion: 0.27
Nodes (12): A2A Server (Planner), A2A Server (Services), Agent Cards, Database, Invoice Agent, MCP Server, MCP tools, Music Agent (+4 more)

### Community 8 - "Orchestrator V2"
Cohesion: 0.23
Nodes (7): extract_structured(), get_agents(), get_planner(), multi_task_node(), planner_node(), Safely pull structured_response out of an agent's ainvoke return value.     Rais, single_task_node()

### Community 9 - "Orchestrator V1 (Legacy)"
Cohesion: 0.33
Nodes (7): aggregator_node(), multi_task_node(), OrchestratorState, route_after_planner(), single_task_node(), OrchestratorState, TypedDict

### Community 10 - "Music Agent"
Cohesion: 0.29
Nodes (5): init_music_agent(), music_agent_response(), Response to user using this format, Response to user using this format, ResponseFormat

### Community 11 - "Test Orchestrator"
Cohesion: 0.83
Nodes (2): main(), send_message()

### Community 12 - "Refund Agent"
Cohesion: 0.5
Nodes (2): process_refund(), Processes a refund for a customer. This is a sensitive action!

### Community 13 - "Database Layer"
Cohesion: 0.5
Nodes (2): get_engine_for_chinook_db(), Pull SQL file, populate in-memory database, and create engine.          Download

## Ambiguous Edges - Review These
- `A2A Server (Planner)` → `A2A Server (Services)`  [AMBIGUOUS]
  assets/MultiAgentSystem.png · relation: conceptually_related_to

## Knowledge Gaps
- **38 isolated node(s):** `Initializes and manages an MCP ClientSession based on the specified transport.`, `Calls the 'find_agent' tool on the connected MCP server.      Args:         sess`, `Reads a resource from the connected MCP server.      Args:         session: The`, `Calls the 'get_tracks_by_artist' tool on the connected MCP server.      Args:`, `Calls the 'get_invoices_by_customer_sorted_by_date' tool on the connected MCP se` (+33 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Test Orchestrator`** (4 nodes): `test_orchestrator.py`, `main()`, `test_orchestrator.py`, `send_message()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Refund Agent`** (4 nodes): `process_refund()`, `Processes a refund for a customer. This is a sensitive action!`, `refund_agent.py`, `refund_agent.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Database Layer`** (4 nodes): `get_engine_for_chinook_db()`, `Pull SQL file, populate in-memory database, and create engine.          Download`, `get_database.py`, `get_database.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `A2A Server (Planner)` and `A2A Server (Services)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `ServerConfig` connect `Common Types & Utils` to `Invoice Agent`?**
  _High betweenness centrality (0.267) - this node is a cross-community bridge._
- **Why does `get_mcp_server_config()` connect `Common Types & Utils` to `Workflow Core`?**
  _High betweenness centrality (0.230) - this node is a cross-community bridge._
- **Why does `BaseAgent` connect `Agent Executor` to `Invoice Agent`?**
  _High betweenness centrality (0.209) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `GenericAgentExecutor` (e.g. with `BaseAgent` and `Get the agent, given an agent card.`) actually correct?**
  _`GenericAgentExecutor` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `ServerConfig` (e.g. with `get_mcp_server_config()` and `Initialize the API key for Google Generative AI.`) actually correct?**
  _`ServerConfig` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Initializes and manages an MCP ClientSession based on the specified transport.`, `Calls the 'find_agent' tool on the connected MCP server.      Args:         sess`, `Reads a resource from the connected MCP server.      Args:         session: The` to the rest of the system?**
  _38 weakly-connected nodes found - possible documentation gaps or missing edges._