# Graph Report - .  (2026-05-13)

## Corpus Check
- Corpus is ~8,305 words - fits in a single context window. You may not need a graph.

## Summary
- 302 nodes · 432 edges · 46 communities (40 shown, 6 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 80 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_System Architecture|System Architecture]]
- [[_COMMUNITY_Planner Core|Planner Core]]
- [[_COMMUNITY_Music Agent|Music Agent]]
- [[_COMMUNITY_A2A Clients|A2A Clients]]
- [[_COMMUNITY_Server Setup|Server Setup]]
- [[_COMMUNITY_Planner Orchestration|Planner Orchestration]]
- [[_COMMUNITY_Invoice Agent|Invoice Agent]]
- [[_COMMUNITY_MCP Database Tools|MCP Database Tools]]
- [[_COMMUNITY_Aggregation Logic|Aggregation Logic]]
- [[_COMMUNITY_Planner HITL Flow|Planner HITL Flow]]
- [[_COMMUNITY_MCP Server Runtime|MCP Server Runtime]]
- [[_COMMUNITY_MCP Tool Wrapper|MCP Tool Wrapper]]
- [[_COMMUNITY_Planner Output Contract|Planner Output Contract]]
- [[_COMMUNITY_Planner CLI|Planner CLI]]
- [[_COMMUNITY_Planner Graph Tests|Planner Graph Tests]]
- [[_COMMUNITY_Configuration Settings|Configuration Settings]]
- [[_COMMUNITY_Planner State|Planner State]]
- [[_COMMUNITY_Shared Constants|Shared Constants]]
- [[_COMMUNITY_Music Executor|Music Executor]]
- [[_COMMUNITY_Execution Statuses|Execution Statuses]]

## God Nodes (most connected - your core abstractions)
1. `MusicAgent` - 21 edges
2. `PlannerAgent` - 21 edges
3. `InvoiceAgent` - 13 edges
4. `build_graph()` - 10 edges
5. `MCPToolAgent` - 10 edges
6. `MusicA2AClient` - 10 edges
7. `InvoiceA2AClient` - 9 edges
8. `AggregatorAgent` - 9 edges
9. `MusicAgentResponse` - 9 edges
10. `InvoiceAgentResponse` - 8 edges

## Surprising Connections (you probably didn't know these)
- `A2A Response Text Extraction` --implements--> `A2A Protocol`  [INFERRED]
  src/multi_agent_system/a2a_client/base.py → PROJECT.md
- `LLM` --conceptually_related_to--> `Planner CLI Main Loop`  [AMBIGUOUS]
  PROJECT.md → scripts/run_planner.py
- `README Project Structure` --semantically_similar_to--> `Multi-Agent System Using LangGraph`  [INFERRED] [semantically similar]
  README.md → PROJECT.md
- `Invoice A2A Server Main` --implements--> `Invoice Agent`  [INFERRED]
  src/multi_agent_system/a2a_servers/invoice_agent/server.py → PROJECT.md
- `Invoice Agent Implementation` --implements--> `Invoice Agent`  [INFERRED]
  src/multi_agent_system/a2a_servers/invoice_agent/agent.py → PROJECT.md

## Hyperedges (group relationships)
- **Multi-Agent Architecture** — PROJECT_mcp_server, PROJECT_a2a_protocol, PROJECT_planner_agent, PROJECT_aggregator_agent, PROJECT_invoice_agent, PROJECT_music_agent [EXTRACTED 1.00]
- **Invoice Agent Intent Tool Contract** — invoice_prompts_system_prompt, invoice_agent_intents, invoice_agent_mcp_tool_calls, invoice_agent_InvoiceRequest, invoice_schemas_InvoiceAgentResponse [EXTRACTED 1.00]
- **A2A Client Server Pairing** — base_BaseA2AClient, invoice_client_InvoiceA2AClient, music_client_MusicA2AClient, invoice_server_create_app, PROJECT_a2a_protocol [INFERRED 0.80]
- **Music Request Classification And Tool Flow** — music_prompt_music_agent_system_prompt, music_executor_musicagentexecutor, music_schemas_musicagentresponse, music_tools_get_tracks_by_artist, music_tools_get_albums_by_artist, music_tools_get_songs_by_genre, music_tools_check_for_songs [INFERRED 0.82]
- **MCP SQL Tool Registry** — mcp_server_create_mcp_server, mcp_db_get_db, invoice_tools_register_invoice_tools, music_tools_register_music_tools, external_fastmcp, external_sqldatabase [EXTRACTED 1.00]
- **Aggregator Structured Result Formatting** — aggregator_agent_aggregatoragent, aggregator_agent_invoke, aggregator_agent_try_parse_json, aggregator_agent_format_structured_result, aggregator_schemas_agentresult, aggregator_schemas_aggregatorinput, aggregator_schemas_aggregatoroutput [EXTRACTED 1.00]
- **Planner Output Contract** — prompts_PLANNER_SYSTEM_PROMPT, schemas_PlannerOutput, schemas_PlannedTask, planner_agent_normalize_output, planner_agent_validate_llm_output [EXTRACTED 1.00]
- **Planner App Execution Flow** — planner_app_graph_build_graph, planner_app_nodes_planner_node, planner_app_nodes_missing_info_node, planner_app_nodes_invoice_node, planner_app_nodes_music_node, planner_app_nodes_final_response_node, planner_app_edges_route_after_planner, planner_app_edges_route_after_invoice [EXTRACTED 1.00]
- **Manual Integration Smoke Scripts** — tests_test_llm_planner, tests_test_llm_planner_raw, tests_test_planner_graph, tests_test_planner_hitl, tests_test_a2a_clients, tests_test_invoice_a2a_client, tests_test_music_a2a_client, tests_test_mcp_tools [INFERRED 0.78]

## Communities (46 total, 6 thin omitted)

### Community 0 - "System Architecture"
Cohesion: 0.07
Nodes (45): A2A Protocol, Agent Cards, Aggregator Agent, Project Configuration, Human-in-the-Loop, Invoice Agent, LangGraph, LLM (+37 more)

### Community 1 - "Planner Core"
Cohesion: 0.15
Nodes (7): PlannerAgent, PlannedTask, PlannerOutput, RuntimeError, main(), main(), run_case()

### Community 2 - "Music Agent"
Cohesion: 0.14
Nodes (5): MCPToolAgent, MusicAgent, MusicRequest, MusicAgentExecutor, MusicAgentResponse

### Community 3 - "A2A Clients"
Cohesion: 0.11
Nodes (6): A2AClientError, BaseA2AClient, InvoiceA2AClient, MusicA2AClient, BaseA2AClient, main()

### Community 4 - "Server Setup"
Cohesion: 0.11
Nodes (16): load_agent_card(), Registered A2A Agent Identifiers, get_llm(), Model Provider Settings, a2a AgentExecutor, A2A DefaultRequestHandler, FastAPI Application, MusicAgent (+8 more)

### Community 5 - "Planner Orchestration"
Cohesion: 0.17
Nodes (18): AgentResult, AggregatorAgent, InvoiceA2AClient, MusicA2AClient, route_after_invoice(), route_after_planner(), build_graph(), _extract_instruction_number() (+10 more)

### Community 6 - "Invoice Agent"
Cohesion: 0.18
Nodes (5): AgentExecutor, InvoiceAgent, InvoiceRequest, InvoiceAgentExecutor, InvoiceAgentResponse

### Community 7 - "MCP Database Tools"
Cohesion: 0.26
Nodes (17): Chinook Invoice Tables, Chinook Music Tables, FastMCP, SQLDatabase, get_employee_by_invoice_and_customer, get_invoices_by_customer_sorted_by_date, get_invoices_sorted_by_unit_price, register_invoice_tools (+9 more)

### Community 8 - "Aggregation Logic"
Cohesion: 0.24
Nodes (10): AggregatorAgent, AggregatorAgent._format_structured_result, AggregatorAgent.invoke, AggregatorAgent._try_parse_json, AgentResult, AggregatorInput, AggregatorOutput, BaseModel (+2 more)

### Community 9 - "Planner HITL Flow"
Cohesion: 0.21
Nodes (13): PlannerAgent Instruction Builders, PlannerAgent Intent Detection Helpers, PlannerAgent.invoke, PlannerAgent._invoke_deterministic, PlannerAgent Missing Field Detection, planner_graph, ask_for_missing_info(), extract_missing_fields() (+5 more)

### Community 10 - "MCP Server Runtime"
Cohesion: 0.2
Nodes (6): get_db(), create_mcp_server(), main(), main(), register_invoice_tools(), register_music_tools()

### Community 11 - "MCP Tool Wrapper"
Cohesion: 0.24
Nodes (5): MCPToolAgent.call_tool, MCPToolAgent, MCPToolAgent._parse_text_result, MCPToolAgent._unwrap_mcp_result, MultiServerMCPClient

### Community 12 - "Planner Output Contract"
Cohesion: 0.28
Nodes (9): PlannerAgent, PlannerAgent.debug_raw_llm, PlannerAgent._invoke_llm, PlannerAgent._normalize_output, PlannerAgent._validate_llm_output, PLANNER_SYSTEM_PROMPT, PlannedTask, PlannerOutput (+1 more)

### Community 13 - "Planner CLI"
Cohesion: 0.83
Nodes (3): create_thread_config(), get_interrupt_question(), main()

## Ambiguous Edges - Review These
- `LLM` → `Planner CLI Main Loop`  [AMBIGUOUS]
  PROJECT.md · relation: conceptually_related_to

## Knowledge Gaps
- **26 isolated node(s):** `Shared constants used across the orchestration system.`, `Project Configuration`, `README Project Structure`, `Invoice A2A Runner Entrypoint`, `MCP Server Runner Entrypoint` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `LLM` and `Planner CLI Main Loop`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `final_response_node()` connect `Planner Orchestration` to `Aggregation Logic`?**
  _High betweenness centrality (0.139) - this node is a cross-community bridge._
- **Why does `AggregatorInput` connect `Aggregation Logic` to `Planner Orchestration`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Why does `build_graph()` connect `Planner Orchestration` to `Planner HITL Flow`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `MusicAgent` (e.g. with `MCPToolAgent` and `MusicAgentResponse`) actually correct?**
  _`MusicAgent` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `PlannerAgent` (e.g. with `PlannedTask` and `PlannerOutput`) actually correct?**
  _`PlannerAgent` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `InvoiceAgent` (e.g. with `MCPToolAgent` and `InvoiceAgentResponse`) actually correct?**
  _`InvoiceAgent` has 4 INFERRED edges - model-reasoned connections that need verification._