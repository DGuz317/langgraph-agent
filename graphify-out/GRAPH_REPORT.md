# Graph Report - langgraph-agent  (2026-05-11)

## Corpus Check
- 63 files · ~8,098 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 370 nodes · 468 edges · 71 communities (61 shown, 10 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 97 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `84a13f60`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]

## God Nodes (most connected - your core abstractions)
1. `PlannerAgent` - 24 edges
2. `MusicAgent` - 21 edges
3. `InvoiceAgent` - 13 edges
4. `MusicA2AClient` - 11 edges
5. `InvoiceA2AClient` - 10 edges
6. `MCPToolAgent` - 10 edges
7. `MusicAgentResponse` - 9 edges
8. `BaseA2AClient` - 8 edges
9. `create_mcp_server()` - 8 edges
10. `MusicAgentExecutor` - 8 edges

## Surprising Connections (you probably didn't know these)
- `latest invoice SQL query` --semantically_similar_to--> `recent invoice query`  [INFERRED] [semantically similar]
  tests/test_mcp_tools.py → README.md
- `Get latest invoice user message` --semantically_similar_to--> `recent invoice query`  [INFERRED] [semantically similar]
  tests/test_invoice_a2a_client.py → README.md
- `get_db database connection` --conceptually_related_to--> `Chinook database`  [INFERRED]
  tests/test_mcp_tools.py → README.md
- `Invoice table` --conceptually_related_to--> `Chinook database`  [INFERRED]
  tests/test_mcp_tools.py → README.md
- `main()` --calls--> `PlannerAgent`  [INFERRED]
  tests/test_llm_planner_raw.py → src/multi_agent_system/planner/agent.py

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

## Communities (71 total, 10 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (10): MCPToolAgent, MCPToolAgent, MusicAgent, MusicRequest, MusicAgentExecutor, MusicAgentResponse, main(), main() (+2 more)

### Community 1 - "Community 1"
Cohesion: 0.09
Nodes (13): A2AClientError, BaseA2AClient, InvoiceA2AClient, MusicA2AClient, BaseA2AClient, ask_for_missing_info(), extract_missing_fields(), interrupt_for_missing_info() (+5 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (8): get_llm(), PlannerAgent, PlannedTask, PlannerOutput, RuntimeError, main(), main(), run_case()

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (30): ADK web Customer Service Agent, Agent cards, Agents package, Chinook database, Common components, Graphify outputs, langgraph-agent, MCP server package (+22 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (25): get_employee_by_invoice_and_customer, get_invoices_by_customer_sorted_by_date, get_invoices_sorted_by_unit_price, register_invoice_tools, get_db(), Configured SQLite Database URI, create_mcp_server(), Multi Agent System MCP Server FastMCP Instance (+17 more)

### Community 5 - "Community 5"
Cohesion: 0.13
Nodes (16): load_agent_card(), A2A Agent Card and JSON-RPC Routes, invoice_agent.json Agent Card, AgentExecutor Base, create_app, DefaultRequestHandler, InvoiceAgentExecutor, InvoiceAgentExecutor.cancel (+8 more)

### Community 6 - "Community 6"
Cohesion: 0.18
Nodes (5): AgentExecutor, InvoiceAgent, InvoiceRequest, InvoiceAgentExecutor, InvoiceAgentResponse

### Community 7 - "Community 7"
Cohesion: 0.13
Nodes (18): Agent Cards, Aggregate Response, Database, Delegated Tasks, Invoice Agent, A2A Server with Planner Agent, MCP Server, MCP Tools (+10 more)

### Community 8 - "Community 8"
Cohesion: 0.16
Nodes (17): InvoiceAgent.ainvoke, EventQueue A2A Response Output, InvoiceAgentExecutor.execute, InvoiceAgent._extract_number, InvoiceAgent._get_invoices_by_unit_price, InvoiceAgent._get_latest_invoice, InvoiceAgent._get_support_employee, InvoiceAgentResponse (+9 more)

### Community 9 - "Community 9"
Cohesion: 0.17
Nodes (11): 1. Start the system, 2. Navigate to Customer Service Agent tab, code:bash (.), code:bash ($projectPath = "...\langraph_agent"), code:bash (.\start_system.ps1), Example question:, langgraph-agent, Project Structure (+3 more)

### Community 10 - "Community 10"
Cohesion: 0.32
Nodes (6): AggregatorAgent, AgentResult, AggregatorInput, AggregatorOutput, BaseModel, final_response_node()

### Community 11 - "Community 11"
Cohesion: 0.25
Nodes (8): A2A Agent Card, Agent Cards Directory, Load Agent Card, A2A Endpoint Settings, .env Settings Configuration, MCP Server URL Setting, Application Settings, Registered A2A Agent Identifiers

### Community 12 - "Community 12"
Cohesion: 0.33
Nodes (6): Architecture or Codebase Questions, GRAPH_REPORT.md, Graphify Knowledge Graph, graphify-out Directory, Raw File Reading, graphify-out/wiki/index.md

### Community 13 - "Community 13"
Cohesion: 0.67
Nodes (6): Cross-module Relationship Questions, EXTRACTED and INFERRED Edges, graphify explain Command, graphify path Command, graphify query Command, grep

### Community 14 - "Community 14"
Cohesion: 0.4
Nodes (5): Graph Node Names, Build Graph, Compiled LangGraph Graph, Conditional Aggregation Route, StateGraph Builder API

### Community 20 - "Community 20"
Cohesion: 0.67
Nodes (3): AST-only Graph Update, Code File Modification, graphify update Command

## Knowledge Gaps
- **55 isolated node(s):** `Shared constants used across the orchestration system.`, `Requirements`, `code:bash (.)`, `code:bash ($projectPath = "...\langraph_agent")`, `code:bash (.\start_system.ps1)` (+50 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MusicAgentExecutor` connect `Community 0` to `Community 5`, `Community 6`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Why does `create_app()` connect `Community 5` to `Community 0`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `PlannerAgent` (e.g. with `PlannedTask` and `PlannerOutput`) actually correct?**
  _`PlannerAgent` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MusicAgent` (e.g. with `MusicAgentExecutor` and `MCPToolAgent`) actually correct?**
  _`MusicAgent` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `InvoiceAgent` (e.g. with `InvoiceAgentExecutor` and `MCPToolAgent`) actually correct?**
  _`InvoiceAgent` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `MusicA2AClient` (e.g. with `BaseA2AClient` and `main()`) actually correct?**
  _`MusicA2AClient` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `InvoiceA2AClient` (e.g. with `BaseA2AClient` and `main()`) actually correct?**
  _`InvoiceA2AClient` has 3 INFERRED edges - model-reasoned connections that need verification._