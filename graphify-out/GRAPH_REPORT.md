# Graph Report - .  (2026-05-05)

## Corpus Check
- Corpus is ~8,460 words - fits in a single context window. You may not need a graph.

## Summary
- 157 nodes · 208 edges · 11 communities detected
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 22 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Workflow Core|Workflow Core]]
- [[_COMMUNITY_Test Client|Test Client]]
- [[_COMMUNITY_Agent Executor|Agent Executor]]
- [[_COMMUNITY_Music & Planner Agents|Music & Planner Agents]]
- [[_COMMUNITY_MCP Server Tools|MCP Server Tools]]
- [[_COMMUNITY_Common Types & Utils|Common Types & Utils]]
- [[_COMMUNITY_A2A Server & Agents|A2A Server & Agents]]
- [[_COMMUNITY_Orchestrator V2|Orchestrator V2]]
- [[_COMMUNITY_Invoice Agent|Invoice Agent]]
- [[_COMMUNITY_Refund Agent|Refund Agent]]
- [[_COMMUNITY_Database Layer|Database Layer]]

## God Nodes (most connected - your core abstractions)
1. `GenericAgentExecutor` - 12 edges
2. `WorkflowGraph` - 10 edges
3. `ServerConfig` - 10 edges
4. `main()` - 9 edges
5. `Orchestrator Agent` - 8 edges
6. `WorkflowNode` - 7 edges
7. `BaseAgent` - 7 edges
8. `init_session()` - 6 edges
9. `get_mcp_server_config()` - 6 edges
10. `A2A Server (Services)` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Initialize the API key for Google Generative AI.` --uses--> `ServerConfig`  [INFERRED]
  src/agent_app/common/utils.py → src/agent_app/common/types.py
- `Configure basic logging.` --uses--> `ServerConfig`  [INFERRED]
  src/agent_app/common/utils.py → src/agent_app/common/types.py
- `Logger specific config, avoiding clutter in enabling all loggging.` --uses--> `ServerConfig`  [INFERRED]
  src/agent_app/common/utils.py → src/agent_app/common/types.py
- `Get the MCP server configuration.` --uses--> `ServerConfig`  [INFERRED]
  src/agent_app/common/utils.py → src/agent_app/common/types.py
- `Get the agent, given an agent card.` --uses--> `GenericAgentExecutor`  [INFERRED]
  src/agent_app/agents/__main__.py → src/agent_app/common/agent_executor.py

## Hyperedges (group relationships)
- **Service Agents Exposed by A2A** — multiagentsystem_refund_agent, multiagentsystem_music_agent, multiagentsystem_invoice_agent [EXTRACTED 0.97]

## Communities

### Community 0 - "Workflow Core"
Cohesion: 0.13
Nodes (9): Represents a graph of workflow nodes., Represents the status of a workflow and its associated node., Represents a single node in a workflow graph.      Each node encapsulates a spec, Status, WorkflowGraph, WorkflowNode, Enum, main() (+1 more)

### Community 1 - "Test Client"
Cohesion: 0.18
Nodes (16): cli(), find_agent(), find_resource(), get_invoices_by_customer_sorted_by_date(), get_tracks_by_artist(), init_session(), main(), Reads a resource from the connected MCP server.      Args:         session: The (+8 more)

### Community 2 - "Agent Executor"
Cohesion: 0.14
Nodes (10): ABC, AgentExecutor, get_agent(), main(), Get the agent, given an agent card., Starts an Agent server., GenericAgentExecutor, AgentExecutor used by invoice agents and music agent (+2 more)

### Community 3 - "Music & Planner Agents"
Cohesion: 0.14
Nodes (12): music_agent_response(), Response to user using this format, ResponseFormat, Response to user using this format, ResponseFormat, BaseModel, AgentResponse, PlannerTask (+4 more)

### Community 4 - "MCP Server Tools"
Cohesion: 0.17
Nodes (15): check_for_songs(), get_albums_by_artist(), get_employee_by_invoice_and_customer(), get_invoices_by_customer_sorted_by_date(), get_invoices_sorted_by_unit_price(), get_songs_by_genre(), get_tracks_by_artist(), main() (+7 more)

### Community 5 - "Common Types & Utils"
Cohesion: 0.27
Nodes (11): Server Confgiguration., ServerConfig, config_logger(), config_logging(), get_mcp_server_config(), init_api_key(), Initialize the API key for Google Generative AI., Configure basic logging. (+3 more)

### Community 6 - "A2A Server & Agents"
Cohesion: 0.27
Nodes (12): A2A Server (Planner), A2A Server (Services), Agent Cards, Database, Invoice Agent, MCP Server, MCP tools, Music Agent (+4 more)

### Community 7 - "Orchestrator V2"
Cohesion: 0.39
Nodes (6): aggregator_node(), multi_task_node(), OrchestratorState, route_after_planner(), single_task_node(), TypedDict

### Community 8 - "Invoice Agent"
Cohesion: 0.5
Nodes (3): invoice_agent_response(), Response to user using this format, ResponseFormat

### Community 9 - "Refund Agent"
Cohesion: 0.5
Nodes (2): process_refund(), Processes a refund for a customer. This is a sensitive action!

### Community 10 - "Database Layer"
Cohesion: 0.5
Nodes (2): get_engine_for_chinook_db(), Pull SQL file, populate in-memory database, and create engine.          Download

## Ambiguous Edges - Review These
- `A2A Server (Planner)` → `A2A Server (Services)`  [AMBIGUOUS]
  assets/MultiAgentSystem.png · relation: conceptually_related_to

## Knowledge Gaps
- **29 isolated node(s):** `Initializes and manages an MCP ClientSession based on the specified transport.`, `Calls the 'find_agent' tool on the connected MCP server.      Args:         sess`, `Reads a resource from the connected MCP server.      Args:         session: The`, `Calls the 'get_tracks_by_artist' tool on the connected MCP server.      Args:`, `Calls the 'get_invoices_by_customer_sorted_by_date' tool on the connected MCP se` (+24 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Refund Agent`** (4 nodes): `process_refund()`, `Processes a refund for a customer. This is a sensitive action!`, `refund_agent.py`, `refund_agent.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Database Layer`** (4 nodes): `get_engine_for_chinook_db()`, `Pull SQL file, populate in-memory database, and create engine.          Download`, `get_database.py`, `get_database.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.