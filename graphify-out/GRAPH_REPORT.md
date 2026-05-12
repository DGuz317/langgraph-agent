# Graph Report - .  (2026-05-12)

## Corpus Check
- Corpus is ~10,540 words - fits in a single context window. You may not need a graph.

## Summary
- 363 nodes · 500 edges · 23 communities detected
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 110 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Project Architecture|Project Architecture]]
- [[_COMMUNITY_Planner Runtime|Planner Runtime]]
- [[_COMMUNITY_MCP Music Agent|MCP Music Agent]]
- [[_COMMUNITY_Planner Intent Logic|Planner Intent Logic]]
- [[_COMMUNITY_A2A Client Layer|A2A Client Layer]]
- [[_COMMUNITY_Aggregator Results|Aggregator Results]]
- [[_COMMUNITY_Aggregator Schemas|Aggregator Schemas]]
- [[_COMMUNITY_MCP Invoice Tools|MCP Invoice Tools]]
- [[_COMMUNITY_Music Agent Logic|Music Agent Logic]]
- [[_COMMUNITY_A2A Server Executors|A2A Server Executors]]
- [[_COMMUNITY_System Diagram|System Diagram]]
- [[_COMMUNITY_MCP Server Tests|MCP Server Tests]]
- [[_COMMUNITY_A2A Client Methods|A2A Client Methods]]
- [[_COMMUNITY_HITL Missing Fields|HITL Missing Fields]]
- [[_COMMUNITY_Planner CLI|Planner CLI]]
- [[_COMMUNITY_Runtime Settings|Runtime Settings]]
- [[_COMMUNITY_Planner State|Planner State]]
- [[_COMMUNITY_Shared Constants|Shared Constants]]
- [[_COMMUNITY_README Workflow|README Workflow]]
- [[_COMMUNITY_MCP Entrypoint|MCP Entrypoint]]
- [[_COMMUNITY_Music Entrypoint|Music Entrypoint]]
- [[_COMMUNITY_LLM Provider|LLM Provider]]
- [[_COMMUNITY_Planner Agent|Planner Agent]]

## God Nodes (most connected - your core abstractions)
1. `MusicAgent` - 21 edges
2. `PlannerAgent` - 21 edges
3. `InvoiceAgent` - 13 edges
4. `MusicA2AClient` - 10 edges
5. `MCPToolAgent` - 9 edges
6. `InvoiceA2AClient` - 9 edges
7. `MusicAgentResponse` - 9 edges
8. `BaseA2AClient.ask` - 9 edges
9. `PlannerOutput` - 9 edges
10. `InvoiceAgentResponse` - 8 edges

## Surprising Connections (you probably didn't know these)
- `MusicAgent` --implements--> `Music Agent`  [INFERRED]
  src/multi_agent_system/a2a_servers/music_agent/agent.py → PROJECT.md
- `InvoiceAgent` --implements--> `Invoice Agent`  [INFERRED]
  src/multi_agent_system/a2a_servers/invoice_agent/agent.py → PROJECT.md
- `get_interrupt_question` --implements--> `Human In The Loop`  [INFERRED]
  scripts/run_planner.py → PROJECT.md
- `Settings` --references--> `MCP Server`  [EXTRACTED]
  src/multi_agent_system/config.py → PROJECT.md
- `Settings` --references--> `A2A Services`  [EXTRACTED]
  src/multi_agent_system/config.py → PROJECT.md

## Hyperedges (group relationships)
- **Invoice A2A Service Flow** — run_invoice_a2a_main_entrypoint, server_main, server_create_app, executor_execute, invoice_agent_ainvoke [EXTRACTED 1.00]
- **Invoice MCP Tool Flow** — invoice_agent_get_latest_invoice, invoice_agent_tool_get_invoices_by_customer_sorted_by_date, invoice_agent_get_invoices_by_unit_price, invoice_agent_tool_get_invoices_sorted_by_unit_price, invoice_agent_get_support_employee, invoice_agent_tool_get_employee_by_invoice_and_customer [EXTRACTED 1.00]
- **Music MCP Tool Flow** — music_agent_get_albums_by_artist, music_agent_tool_get_albums_by_artist, music_agent_get_tracks_by_artist, music_agent_tool_get_tracks_by_artist, music_agent_get_songs_by_genre, music_agent_tool_get_songs_by_genre, music_agent_check_song, music_agent_tool_check_for_songs [EXTRACTED 1.00]
- **Music Agent Intent To MCP Tool Flow** — prompts_MusicAgentSystemPrompt, prompts_tracks_by_artist_intent, prompts_albums_by_artist_intent, prompts_songs_by_genre_intent, prompts_check_song_intent, music_tools_get_tracks_by_artist, music_tools_get_albums_by_artist, music_tools_get_songs_by_genre, music_tools_check_for_songs [EXTRACTED 1.00]
- **MCP Server Tool Registration Flow** — mcp_server_create_mcp_server, db_get_db, mcp_server_MultiAgentMCPServer, invoice_tools_register_invoice_tools, music_tools_register_music_tools, mcp_tools_SQLDatabaseChinookData [EXTRACTED 1.00]
- **Structured JSON Result Flow** — schemas_MusicAgentResponse, executor_a2a_text_response, aggregator_agent_try_parse_json, aggregator_agent_format_structured_result, aggregator_agent_structured_result_envelope, mcp_tool_agent_parse_text_result [INFERRED 0.80]
- **Planner State Graph Flow** — graph_build_graph, nodes_planner_node, edges_route_after_planner, nodes_missing_info_node, nodes_invoice_node, nodes_music_node, nodes_final_response_node, state_PlannerAppState [EXTRACTED 1.00]
- **Missing Information Resume Flow** — edges_route_after_planner, nodes_missing_info_node, hitl_interrupt_for_missing_info, hitl_extract_missing_fields, state_PlannerAppState, test_planner_hitl_PlannerGraphResumeFlow [EXTRACTED 1.00]
- **Invoice Music Aggregation Flow** — edges_route_after_invoice, nodes_invoice_node, nodes_music_node, nodes_final_response_node, nodes_AggregatorInvocation, schemas_PlannerOutput [EXTRACTED 1.00]
- **User Orchestrator Query Response** — multiagentsystem_user, multiagentsystem_orchestrator_agent, multiagentsystem_a2a_server_planner [EXTRACTED 0.80]
- **Specialist Agent Group** — multiagentsystem_a2a_server_specialists, multiagentsystem_refund_agent, multiagentsystem_music_agent, multiagentsystem_invoice_agent [EXTRACTED 1.00]
- **MCP Resource Group** — multiagentsystem_mcp_server, multiagentsystem_mcp_tools, multiagentsystem_agent_cards, multiagentsystem_database [EXTRACTED 1.00]

## Communities

### Community 0 - "Project Architecture"
Cohesion: 0.08
Nodes (33): A2A Services, Agent Cards, Aggregator Agent, Human In The Loop, Invoice Agent, MCP Server, Multi-Agent System, Music Agent (+25 more)

### Community 1 - "Planner Runtime"
Cohesion: 0.1
Nodes (33): PlannerAgent.debug_raw_llm, PlannerAgent intent detection helpers, PlannerAgent.invoke, PlannerAgent._invoke_deterministic, PlannerAgent._invoke_llm, PlannerAgent missing field extraction helpers, PlannerAgent._normalize_output, PlannerAgent._validate_llm_output (+25 more)

### Community 2 - "MCP Music Agent"
Cohesion: 0.13
Nodes (7): MCPToolAgent, MusicAgent, MusicRequest, MusicAgentResponse, main(), run_case(), main()

### Community 3 - "Planner Intent Logic"
Cohesion: 0.13
Nodes (8): get_llm(), PlannerAgent, PlannedTask, PlannerOutput, RuntimeError, main(), main(), run_case()

### Community 4 - "A2A Client Layer"
Cohesion: 0.11
Nodes (11): A2AClientError, BaseA2AClient, InvoiceA2AClient, MusicA2AClient, BaseA2AClient, _extract_instruction_number(), invoice_node(), missing_info_node() (+3 more)

### Community 5 - "Aggregator Results"
Cohesion: 0.08
Nodes (29): AggregatorAgent, AggregatorAgent._format_structured_result, AggregatorAgent.invoke, Structured Result Envelope success/content/data, AggregatorAgent._try_parse_json, AgentResult, AggregatorInput, AggregatorOutput (+21 more)

### Community 6 - "Aggregator Schemas"
Cohesion: 0.15
Nodes (10): AggregatorAgent, AgentResult, AggregatorInput, AggregatorOutput, BaseModel, InvoiceAgent, InvoiceRequest, InvoiceAgentResponse (+2 more)

### Community 7 - "MCP Invoice Tools"
Cohesion: 0.16
Nodes (23): get_db, get_employee_by_invoice_and_customer, get_invoices_by_customer_sorted_by_date, get_invoices_sorted_by_unit_price, register_invoice_tools, Multi Agent System MCP Server, create_mcp_server, MCPToolAgent (+15 more)

### Community 8 - "Music Agent Logic"
Cohesion: 0.1
Nodes (21): MusicAgent.ainvoke, MusicAgent._check_song, MusicAgent._clean_extracted_value, MusicAgent._extract_after_keywords, MusicAgent._extract_genre, MusicAgent._extract_song_title, MusicAgent._get_albums_by_artist, MusicAgent._get_songs_by_genre (+13 more)

### Community 9 - "A2A Server Executors"
Cohesion: 0.12
Nodes (8): AgentExecutor, load_agent_card(), InvoiceAgentExecutor, create_app(), main(), MusicAgentExecutor, create_app(), main()

### Community 10 - "System Diagram"
Cohesion: 0.2
Nodes (12): A2A Server Planner, A2A Server Specialists, Agent Cards, Database, Invoice Agent, MCP Server, MCP tools, Music Agent (+4 more)

### Community 11 - "MCP Server Tests"
Cohesion: 0.2
Nodes (6): get_db(), create_mcp_server(), main(), main(), register_invoice_tools(), register_music_tools()

### Community 12 - "A2A Client Methods"
Cohesion: 0.2
Nodes (11): BaseA2AClient.ask, BaseA2AClient.extract_text, A2A JSON-RPC SendMessage Payload, BaseA2AClient.send_message, InvoiceA2AClient.get_invoices_by_unit_price, InvoiceA2AClient.get_latest_invoice, InvoiceA2AClient.get_support_employee, MusicA2AClient.check_song (+3 more)

### Community 13 - "HITL Missing Fields"
Cohesion: 0.7
Nodes (4): ask_for_missing_info(), extract_missing_fields(), _extract_number(), interrupt_for_missing_info()

### Community 14 - "Planner CLI"
Cohesion: 0.83
Nodes (3): create_thread_config(), get_interrupt_question(), main()

### Community 15 - "Runtime Settings"
Cohesion: 0.67
Nodes (2): BaseSettings, Settings

### Community 17 - "Planner State"
Cohesion: 0.67
Nodes (2): PlannerAppState, TypedDict

### Community 21 - "Shared Constants"
Cohesion: 1.0
Nodes (1): Shared constants used across the orchestration system.

### Community 22 - "README Workflow"
Cohesion: 1.0
Nodes (2): langgraph-agent, Start System PowerShell Workflow

### Community 23 - "MCP Entrypoint"
Cohesion: 1.0
Nodes (2): Run MCP Server Entrypoint, MCP Server main

### Community 24 - "Music Entrypoint"
Cohesion: 1.0
Nodes (2): Run Music A2A Entrypoint, Music A2A server main

### Community 25 - "LLM Provider"
Cohesion: 1.0
Nodes (2): Model Provider Settings, get_llm

### Community 49 - "Planner Agent"
Cohesion: 1.0
Nodes (1): PlannerAgent

## Knowledge Gaps
- **57 isolated node(s):** `Shared constants used across the orchestration system.`, `Agent Cards`, `Planner Graph`, `langgraph-agent`, `Start System PowerShell Workflow` (+52 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Runtime Settings`** (3 nodes): `BaseSettings`, `Settings`, `config.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Planner State`** (3 nodes): `PlannerAppState`, `state.py`, `TypedDict`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Shared Constants`** (2 nodes): `Shared constants used across the orchestration system.`, `constants.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `README Workflow`** (2 nodes): `langgraph-agent`, `Start System PowerShell Workflow`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `MCP Entrypoint`** (2 nodes): `Run MCP Server Entrypoint`, `MCP Server main`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Music Entrypoint`** (2 nodes): `Run Music A2A Entrypoint`, `Music A2A server main`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `LLM Provider`** (2 nodes): `Model Provider Settings`, `get_llm`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Planner Agent`** (1 nodes): `PlannerAgent`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `InvoiceAgentExecutor.execute` connect `Aggregator Results` to `Project Architecture`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `MusicAgent.ainvoke Call` connect `Project Architecture` to `Aggregator Results`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `MusicAgent` (e.g. with `MCPToolAgent` and `MusicAgentResponse`) actually correct?**
  _`MusicAgent` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `PlannerAgent` (e.g. with `PlannedTask` and `PlannerOutput`) actually correct?**
  _`PlannerAgent` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `InvoiceAgent` (e.g. with `MCPToolAgent` and `InvoiceAgentResponse`) actually correct?**
  _`InvoiceAgent` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `MusicA2AClient` (e.g. with `BaseA2AClient` and `main()`) actually correct?**
  _`MusicA2AClient` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MCPToolAgent` (e.g. with `InvoiceRequest` and `InvoiceAgent`) actually correct?**
  _`MCPToolAgent` has 4 INFERRED edges - model-reasoned connections that need verification._