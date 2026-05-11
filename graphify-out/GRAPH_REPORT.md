# Graph Report - .  (2026-05-11)

## Corpus Check
- Corpus is ~6,710 words - fits in a single context window. You may not need a graph.

## Summary
- 296 nodes · 354 edges · 23 communities detected
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 67 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_A2A Client Layer|A2A Client Layer]]
- [[_COMMUNITY_MCP Planner Tools|MCP Planner Tools]]
- [[_COMMUNITY_Project Documentation|Project Documentation]]
- [[_COMMUNITY_Planner Aggregator Schemas|Planner Aggregator Schemas]]
- [[_COMMUNITY_MCP Invoice Tools|MCP Invoice Tools]]
- [[_COMMUNITY_System Architecture|System Architecture]]
- [[_COMMUNITY_Invoice Agent Executor|Invoice Agent Executor]]
- [[_COMMUNITY_Invoice A2A Server|Invoice A2A Server]]
- [[_COMMUNITY_Music Agent Executor|Music Agent Executor]]
- [[_COMMUNITY_Agent Card Settings|Agent Card Settings]]
- [[_COMMUNITY_Graphify Usage Rules|Graphify Usage Rules]]
- [[_COMMUNITY_Graphify Query Commands|Graphify Query Commands]]
- [[_COMMUNITY_LangGraph Builder|LangGraph Builder]]
- [[_COMMUNITY_HITL Missing Info|HITL Missing Info]]
- [[_COMMUNITY_Planner Graph Test|Planner Graph Test]]
- [[_COMMUNITY_Planner Routing Edges|Planner Routing Edges]]
- [[_COMMUNITY_Planner App State|Planner App State]]
- [[_COMMUNITY_Music Client Test|Music Client Test]]
- [[_COMMUNITY_Graph Construction|Graph Construction]]
- [[_COMMUNITY_Graphify Update Workflow|Graphify Update Workflow]]
- [[_COMMUNITY_Execution Statuses|Execution Statuses]]
- [[_COMMUNITY_A2A Client Schemas|A2A Client Schemas]]
- [[_COMMUNITY_Aggregator Agent|Aggregator Agent]]

## God Nodes (most connected - your core abstractions)
1. `MusicAgent` - 21 edges
2. `PlannerAgent` - 14 edges
3. `MusicA2AClient` - 11 edges
4. `InvoiceA2AClient` - 10 edges
5. `MCPToolAgent` - 8 edges
6. `BaseA2AClient` - 8 edges
7. `MusicAgentExecutor` - 8 edges
8. `Configured SQLite Database URI` - 8 edges
9. `MusicAgentResponse` - 7 edges
10. `Project Structure` - 7 edges

## Surprising Connections (you probably didn't know these)
- `latest invoice SQL query` --semantically_similar_to--> `recent invoice query`  [INFERRED] [semantically similar]
  tests/test_mcp_tools.py → README.md
- `Get latest invoice user message` --semantically_similar_to--> `recent invoice query`  [INFERRED] [semantically similar]
  tests/test_invoice_a2a_client.py → README.md
- `get_db database connection` --conceptually_related_to--> `Chinook database`  [INFERRED]
  tests/test_mcp_tools.py → README.md
- `Invoice table` --conceptually_related_to--> `Chinook database`  [INFERRED]
  tests/test_mcp_tools.py → README.md
- `main()` --calls--> `get_tracks_by_artist`  [INFERRED]
  tests/test_a2a_clients.py → src/multi_agent_system/mcp_server/tools/music_tools.py

## Hyperedges (group relationships)
- **Latest Invoice Retrieval Flow** — test_mcp_tools_latest_invoice_sql, test_invoice_a2a_client_user_message_latest_invoice, readme_recent_invoice_query, readme_chinook_database [INFERRED 0.82]
- **Invoice A2A Client Server Flow** — test_invoice_a2a_client_invoice_a2a_url, test_invoice_a2a_client_jsonrpc_payload, test_invoice_a2a_client_sendmessage_method, run_invoice_a2a_invoice_agent_server_main [INFERRED 0.78]
- **Planner Execution Flow** — main_build_graph, nodes_planner_node, nodes_execute_tasks_node, nodes_aggregate_node, state_appstate [EXTRACTED 1.00]
- **External Agent Integration** — config_a2a_endpoint_settings, constants_a2a_agent_identifiers, agent_card_loader_load_agent_card, mcp_tool_agent [INFERRED 0.78]
- **Invoice Agent Request Dispatch Flow** — invoice_agent_ainvoke, invoice_agent_parse_request, invoice_agent_validate_request, invoice_agent_get_latest_invoice, invoice_agent_get_invoices_by_unit_price, invoice_agent_get_support_employee, invoice_agent_invoiceagentresponse [EXTRACTED 1.00]
- **Invoice MCP Query Handlers** — invoice_agent_get_latest_invoice, invoice_agent_get_invoices_by_unit_price, invoice_agent_get_support_employee, invoice_agent_tool_customer_invoices_by_date, invoice_agent_tool_invoices_by_unit_price, invoice_agent_tool_employee_by_invoice_customer [EXTRACTED 1.00]
- **Invoice A2A Service Composition** — invoice_agent_create_app, invoice_agent_fastapi_service, invoice_agent_agent_card, invoice_agent_default_request_handler, invoice_agent_executor, invoice_agent_a2a_routes [EXTRACTED 1.00]
- **MCP Server Tool Registration Pipeline** — mcp_server_server_create_mcp_server, mcp_server_db_get_db, invoice_tools_register_invoice_tools, music_tools_register_music_tools [EXTRACTED 1.00]
- **Invoice Query Tool Suite** — invoice_tools_register_invoice_tools, invoice_tools_get_invoices_by_customer_sorted_by_date, invoice_tools_get_invoices_sorted_by_unit_price, invoice_tools_get_employee_by_invoice_and_customer [EXTRACTED 1.00]
- **Music Catalog Query Tool Suite** — music_tools_register_music_tools, music_tools_get_albums_by_artist, music_tools_get_tracks_by_artist, music_tools_get_songs_by_genre, music_tools_check_for_songs [EXTRACTED 1.00]
- **README Documented System Structure** — readme_langgraph_agent, readme_agent_cards, readme_agents, readme_common_components, readme_chinook_database, readme_mcp_server [EXTRACTED 1.00]
- **Multi-Agent System Message Flow** — MultiAgentSystem_user, MultiAgentSystem_orchestrator_agent, MultiAgentSystem_left_a2a_server, MultiAgentSystem_worker_a2a_server, MultiAgentSystem_mcp_server [EXTRACTED 1.00]
- **A2A Worker Agent Group** — MultiAgentSystem_worker_a2a_server, MultiAgentSystem_refund_agent, MultiAgentSystem_music_agent, MultiAgentSystem_invoice_agent [EXTRACTED 1.00]
- **MCP Server Resources** — MultiAgentSystem_mcp_server, MultiAgentSystem_mcp_tools, MultiAgentSystem_agent_cards, MultiAgentSystem_database [EXTRACTED 1.00]
- **Graphify Navigation Commands** — agents_graphify_query_command, agents_graphify_path_command, agents_graphify_explain_command [EXTRACTED 1.00]

## Communities

### Community 0 - "A2A Client Layer"
Cohesion: 0.09
Nodes (12): A2AClientError, BaseA2AClient, InvoiceA2AClient, MusicA2AClient, BaseA2AClient, final_response_node(), invoice_node(), missing_info_node() (+4 more)

### Community 1 - "MCP Planner Tools"
Cohesion: 0.11
Nodes (7): MCPToolAgent, MCPToolAgent, MusicAgent, MusicRequest, MusicAgentResponse, main(), main()

### Community 2 - "Project Documentation"
Cohesion: 0.08
Nodes (30): ADK web Customer Service Agent, Agent cards, Agents package, Chinook database, Common components, Graphify outputs, langgraph-agent, MCP server package (+22 more)

### Community 3 - "Planner Aggregator Schemas"
Cohesion: 0.15
Nodes (7): AgentResult, AggregatorInput, AggregatorOutput, BaseModel, PlannerAgent, PlannedTask, PlannerOutput

### Community 4 - "MCP Invoice Tools"
Cohesion: 0.16
Nodes (22): get_employee_by_invoice_and_customer, get_invoices_by_customer_sorted_by_date, get_invoices_sorted_by_unit_price, register_invoice_tools, get_db, Configured SQLite Database URI, create_mcp_server, Multi Agent System MCP Server FastMCP Instance (+14 more)

### Community 5 - "System Architecture"
Cohesion: 0.13
Nodes (18): Agent Cards, Aggregate Response, Database, Delegated Tasks, Invoice Agent, A2A Server with Planner Agent, MCP Server, MCP Tools (+10 more)

### Community 6 - "Invoice Agent Executor"
Cohesion: 0.16
Nodes (17): InvoiceAgent.ainvoke, EventQueue A2A Response Output, InvoiceAgentExecutor.execute, InvoiceAgent._extract_number, InvoiceAgent._get_invoices_by_unit_price, InvoiceAgent._get_latest_invoice, InvoiceAgent._get_support_employee, InvoiceAgentResponse (+9 more)

### Community 7 - "Invoice A2A Server"
Cohesion: 0.24
Nodes (11): A2A Agent Card and JSON-RPC Routes, invoice_agent.json Agent Card, AgentExecutor Base, create_app, DefaultRequestHandler, InvoiceAgentExecutor, InvoiceAgentExecutor.cancel, Invoice A2A FastAPI Service (+3 more)

### Community 8 - "Music Agent Executor"
Cohesion: 0.22
Nodes (4): AgentExecutor, MusicAgentExecutor, create_app(), main()

### Community 9 - "Agent Card Settings"
Cohesion: 0.25
Nodes (8): A2A Agent Card, Agent Cards Directory, Load Agent Card, A2A Endpoint Settings, .env Settings Configuration, MCP Server URL Setting, Application Settings, Registered A2A Agent Identifiers

### Community 10 - "Graphify Usage Rules"
Cohesion: 0.33
Nodes (6): Architecture or Codebase Questions, GRAPH_REPORT.md, Graphify Knowledge Graph, graphify-out Directory, Raw File Reading, graphify-out/wiki/index.md

### Community 11 - "Graphify Query Commands"
Cohesion: 0.67
Nodes (6): Cross-module Relationship Questions, EXTRACTED and INFERRED Edges, graphify explain Command, graphify path Command, graphify query Command, grep

### Community 12 - "LangGraph Builder"
Cohesion: 0.4
Nodes (5): Graph Node Names, Build Graph, Compiled LangGraph Graph, Conditional Aggregation Route, StateGraph Builder API

### Community 13 - "HITL Missing Info"
Cohesion: 0.8
Nodes (3): ask_for_missing_info(), extract_missing_fields(), interrupt_for_missing_info()

### Community 14 - "Planner Graph Test"
Cohesion: 0.83
Nodes (2): main(), run_case()

### Community 15 - "Planner Routing Edges"
Cohesion: 0.67
Nodes (2): route_after_invoice(), route_after_planner()

### Community 16 - "Planner App State"
Cohesion: 0.5
Nodes (2): PlannerAppState, TypedDict

### Community 17 - "Music Client Test"
Cohesion: 0.67
Nodes (1): main()

### Community 18 - "Graph Construction"
Cohesion: 0.67
Nodes (1): build_graph()

### Community 19 - "Graphify Update Workflow"
Cohesion: 0.67
Nodes (3): AST-only Graph Update, Code File Modification, graphify update Command

### Community 25 - "Execution Statuses"
Cohesion: 1.0
Nodes (1): Supported Execution Statuses

### Community 29 - "A2A Client Schemas"
Cohesion: 1.0
Nodes (1): Empty A2A Client Schemas Module

### Community 31 - "Aggregator Agent"
Cohesion: 1.0
Nodes (1): Empty Aggregator Agent Module

## Knowledge Gaps
- **47 isolated node(s):** `CustomerId 5`, `SendMessage method`, `A2A JSON headers`, `run_mcp_server entrypoint`, `run_invoice_a2a entrypoint` (+42 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Planner Graph Test`** (4 nodes): `test_planner_graph.py`, `main()`, `test_planner_graph.py`, `run_case()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Planner Routing Edges`** (4 nodes): `edges.py`, `route_after_invoice()`, `route_after_planner()`, `edges.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Planner App State`** (4 nodes): `state.py`, `PlannerAppState`, `state.py`, `TypedDict`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Music Client Test`** (3 nodes): `test_music_a2a_client.py`, `main()`, `test_music_a2a_client.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Graph Construction`** (3 nodes): `graph.py`, `build_graph()`, `graph.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Execution Statuses`** (1 nodes): `Supported Execution Statuses`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `A2A Client Schemas`** (1 nodes): `Empty A2A Client Schemas Module`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Aggregator Agent`** (1 nodes): `Empty Aggregator Agent Module`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MusicAgent` connect `MCP Planner Tools` to `Music Agent Executor`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Why does `MusicAgentExecutor` connect `Music Agent Executor` to `MCP Planner Tools`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `create_app()` connect `Music Agent Executor` to `Invoice A2A Server`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `MusicAgent` (e.g. with `MCPToolAgent` and `MusicAgentResponse`) actually correct?**
  _`MusicAgent` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `PlannerAgent` (e.g. with `PlannedTask` and `PlannerOutput`) actually correct?**
  _`PlannerAgent` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `MusicA2AClient` (e.g. with `BaseA2AClient` and `main()`) actually correct?**
  _`MusicA2AClient` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `InvoiceA2AClient` (e.g. with `BaseA2AClient` and `main()`) actually correct?**
  _`InvoiceA2AClient` has 3 INFERRED edges - model-reasoned connections that need verification._