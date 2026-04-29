# Graph Report - .  (2026-04-28)

## Corpus Check
- Corpus is ~11,105 words - fits in a single context window. You may not need a graph.

## Summary
- 177 nodes · 285 edges · 14 communities detected
- Extraction: 70% EXTRACTED · 29% INFERRED · 0% AMBIGUOUS · INFERRED: 84 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Node Graph Workflow|Node Graph Workflow]]
- [[_COMMUNITY_Respond User This|Respond User This]]
- [[_COMMUNITY_Mcp Get Server|Mcp Get Server]]
- [[_COMMUNITY_Init Config Server|Init Config Server]]
- [[_COMMUNITY_Example Query Mcp|Example Query Mcp]]
- [[_COMMUNITY_Agentexecutor Get Given|Agentexecutor Get Given]]
- [[_COMMUNITY_Server A2a Planner|Server A2a Planner]]
- [[_COMMUNITY_Embeddings Cards Card|Embeddings Cards Card]]
- [[_COMMUNITY_Invoice Music Orchestrator|Invoice Music Orchestrator]]
- [[_COMMUNITY_Invoiceagent Ensure Graph|Invoiceagent Ensure Graph]]
- [[_COMMUNITY_Langgraphplanneragent Ensure Graph|Langgraphplanneragent Ensure Graph]]
- [[_COMMUNITY_Musicagent Ensure Graph|Musicagent Ensure Graph]]
- [[_COMMUNITY_Refund Process Processes|Refund Process Processes]]
- [[_COMMUNITY_Get Engine Database|Get Engine Database]]

## God Nodes (most connected - your core abstractions)
1. `BaseAgent` - 22 edges
2. `OrchestratorAgent` - 16 edges
3. `TaskList` - 15 edges
4. `WorkflowGraph` - 14 edges
5. `InvoiceAgent` - 12 edges
6. `MusicAgent` - 12 edges
7. `GenericAgentExecutor` - 11 edges
8. `WorkflowNode` - 11 edges
9. `LangGraphPlannerAgent` - 11 edges
10. `ServerConfig` - 9 edges

## Surprising Connections (you probably didn't know these)
- `AgentExecutor used by invoice agents and music agent` --uses--> `BaseAgent`  [INFERRED]
  src/agent_app/common/agent_executor.py → src/agent_app/common/base_agent.py
- `main()` --calls--> `send_message()`  [INFERRED]
  test/test_invoice.py → test/test_orchestrator.py
- `main()` --calls--> `send_message()`  [INFERRED]
  test/test_music.py → test/test_orchestrator.py
- `Initialize the API key for Google Generative AI.` --uses--> `ServerConfig`  [INFERRED]
  src/agent_app/common/utils.py → src/agent_app/common/types.py
- `Configure basic logging.` --uses--> `ServerConfig`  [INFERRED]
  src/agent_app/common/utils.py → src/agent_app/common/types.py

## Hyperedges (group relationships)
- **Quickstart Usage Flow** — readme_start_system_ps1, readme_customer_service_agent_tab, readme_local_url_127_0_0_1_8050, readme_adk_web [EXTRACTED 1.00]
- **Example Query Set** — readme_music_recommendation_query, readme_invoice_query, readme_combined_query [EXTRACTED 1.00]
- **Service Agents Exposed by A2A** — multiagentsystem_refund_agent, multiagentsystem_music_agent, multiagentsystem_invoice_agent [EXTRACTED 0.97]

## Communities

### Community 0 - "Node Graph Workflow"
Cohesion: 0.14
Nodes (11): OrchestratorAgent, Add a node to the graph., Execute and stream response., # TODO: Make the graph dynamically iterable over edges, Represents a graph of workflow nodes., Represents the status of a workflow and its associated node., Represents a single node in a workflow graph.      Each node encapsulates a spec, Status (+3 more)

### Community 1 - "Respond User This"
Cohesion: 0.17
Nodes (16): ABC, Respond to the user in this format., ResponseFormat, Respond to the user in this format., ResponseFormat, Respond to the user in this format., ResponseFormat, BaseModel (+8 more)

### Community 2 - "Mcp Get Server"
Cohesion: 0.15
Nodes (16): cli(), find_agent(), find_resource(), get_invoices_by_customer_sorted_by_date(), get_tracks_by_artist(), init_session(), main(), Reads a resource from the connected MCP server.      Args:         session: The (+8 more)

### Community 3 - "Init Config Server"
Cohesion: 0.17
Nodes (11): Server Confgiguration., ServerConfig, config_logger(), config_logging(), get_mcp_server_config(), init_api_key(), Initialize the API key for Google Generative AI., Configure basic logging. (+3 more)

### Community 4 - "Example Query Mcp"
Cohesion: 0.15
Nodes (15): ADK web interface, agent_cards directory, Combined tracks and invoice example query, Customer Service Agent tab, Recent invoice example query, langgraph-agent, http://127.0.0.1:8050, mcp/client.py (+7 more)

### Community 5 - "Agentexecutor Get Given"
Cohesion: 0.21
Nodes (7): AgentExecutor, get_agent(), main(), Get the agent, given an agent card., Starts an Agent server., GenericAgentExecutor, AgentExecutor used by invoice agents and music agent

### Community 6 - "Server A2a Planner"
Cohesion: 0.27
Nodes (12): A2A Server (Planner), A2A Server (Services), Agent Cards, Database, Invoice Agent, MCP Server, MCP tools, Music Agent (+4 more)

### Community 7 - "Embeddings Cards Card"
Cohesion: 0.29
Nodes (9): build_agent_card_embeddings(), generate_embeddings(), load_agent_cards(), main(), Loads agent cards, generates embeddings for them, and returns a DataFrame., Initializes and runs the Agent Cards MCP server.      Args:         host: The ho, Generates embeddings for the given text using local Ollama API.      Args:, Loads agent card data from JSON files within a specified directory.      Returns (+1 more)

### Community 8 - "Invoice Music Orchestrator"
Cohesion: 0.33
Nodes (4): main(), main(), main(), send_message()

### Community 9 - "Invoiceagent Ensure Graph"
Cohesion: 0.52
Nodes (2): InvoiceAgent, InvoiceAgent - specialized for retrieving and processing invoice information.

### Community 10 - "Langgraphplanneragent Ensure Graph"
Cohesion: 0.48
Nodes (3): LangGraphPlannerAgent, Planner Agent backed by LangGraph., BaseAgent

### Community 11 - "Musicagent Ensure Graph"
Cohesion: 0.52
Nodes (2): MusicAgent, MusicAgent - specifically is to focused on helping customers discover and learn

### Community 13 - "Refund Process Processes"
Cohesion: 0.67
Nodes (2): process_refund(), Processes a refund for a customer. This is a sensitive action!

### Community 14 - "Get Engine Database"
Cohesion: 0.67
Nodes (2): get_engine_for_chinook_db(), Pull SQL file, populate in-memory database, and create engine.          Download

## Ambiguous Edges - Review These
- `A2A Server (Planner)` → `A2A Server (Services)`  [AMBIGUOUS]
  assets/MultiAgentSystem.png · relation: conceptually_related_to

## Knowledge Gaps
- **31 isolated node(s):** `Initializes and manages an MCP ClientSession based on the specified transport.`, `Calls the 'find_agent' tool on the connected MCP server.      Args:         sess`, `Reads a resource from the connected MCP server.      Args:         session: The`, `Calls the 'get_tracks_by_artist' tool on the connected MCP server.      Args:`, `Calls the 'get_invoices_by_customer_sorted_by_date' tool on the connected MCP se` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Invoiceagent Ensure Graph`** (7 nodes): `InvoiceAgent`, `._ensure_graph()`, `.fetch_mcp_tools()`, `.get_agent_response()`, `.invoke()`, `.stream()`, `InvoiceAgent - specialized for retrieving and processing invoice information.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Musicagent Ensure Graph`** (7 nodes): `MusicAgent`, `._ensure_graph()`, `.fetch_mcp_tools()`, `.get_agent_response()`, `.invoke()`, `.stream()`, `MusicAgent - specifically is to focused on helping customers discover and learn`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Refund Process Processes`** (3 nodes): `process_refund()`, `Processes a refund for a customer. This is a sensitive action!`, `refund_agent.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Get Engine Database`** (3 nodes): `get_engine_for_chinook_db()`, `Pull SQL file, populate in-memory database, and create engine.          Download`, `get_database.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `A2A Server (Planner)` and `A2A Server (Services)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `BaseAgent` connect `Respond User This` to `Node Graph Workflow`, `Agentexecutor Get Given`, `Invoiceagent Ensure Graph`, `Langgraphplanneragent Ensure Graph`, `Musicagent Ensure Graph`?**
  _High betweenness centrality (0.195) - this node is a cross-community bridge._
- **Why does `WorkflowNode` connect `Node Graph Workflow` to `Mcp Get Server`?**
  _High betweenness centrality (0.143) - this node is a cross-community bridge._
- **Why does `OrchestratorAgent` connect `Node Graph Workflow` to `Respond User This`, `Langgraphplanneragent Ensure Graph`, `Init Config Server`, `Agentexecutor Get Given`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `BaseAgent` (e.g. with `GenericAgentExecutor` and `AgentExecutor used by invoice agents and music agent`) actually correct?**
  _`BaseAgent` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `OrchestratorAgent` (e.g. with `Get the agent, given an agent card.` and `Starts an Agent server.`) actually correct?**
  _`OrchestratorAgent` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `TaskList` (e.g. with `ResponseFormat` and `InvoiceAgent`) actually correct?**
  _`TaskList` has 12 INFERRED edges - model-reasoned connections that need verification._