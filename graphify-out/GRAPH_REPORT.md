# Graph Report - langgraph-agent  (2026-05-14)

## Corpus Check
- 64 files · ~9,364 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 415 nodes · 610 edges · 47 communities (41 shown, 6 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 132 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `91908731`
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
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]

## God Nodes (most connected - your core abstractions)
1. `PlannerAgent` - 36 edges
2. `MusicAgent` - 21 edges
3. `extract_missing_fields()` - 18 edges
4. `PlannerOutput` - 16 edges
5. `PlannedTask` - 14 edges
6. `Multi-Agent System Using LangGraph` - 14 edges
7. `InvoiceAgent` - 13 edges
8. `build_graph()` - 10 edges
9. `MCPToolAgent` - 10 edges
10. `MusicA2AClient` - 10 edges

## Surprising Connections (you probably didn't know these)
- `A2A Response Text Extraction` --implements--> `A2A Protocol`  [INFERRED]
  src/multi_agent_system/a2a_client/base.py → PROJECT.md
- `LLM` --conceptually_related_to--> `Planner CLI Main Loop`  [AMBIGUOUS]
  PROJECT.md → scripts/run_planner.py
- `test_route_after_missing_info_goes_to_music()` --calls--> `route_after_planner()`  [INFERRED]
  tests/test_planner_graph.py → src/multi_agent_system/planner_app/edges.py
- `test_planner_hitl Resume Flow` --references--> `interrupt_for_missing_info()`  [INFERRED]
  tests/test_planner_hitl.py → src/multi_agent_system/planner_app/hitl.py
- `README Project Structure` --semantically_similar_to--> `Multi-Agent System Using LangGraph`  [INFERRED] [semantically similar]
  README.md → PROJECT.md

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

## Communities (47 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (23): PlannerAgent, PlannedTask, PlannerOutput, RuntimeError, main(), main(), run_case(), test_llm_planner_accepts_hitl_context_for_replanning() (+15 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (45): A2A Protocol, Agent Cards, Aggregator Agent, Project Configuration, Human-in-the-Loop, Invoice Agent, LangGraph, LLM (+37 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (36): A2A Clients, A2A Services, Agent Cards, Agents:, Aggregator Agent, Architecture Overview, code:bash (multi-agent-system/), code:python (import json) (+28 more)

### Community 3 - "Community 3"
Cohesion: 0.12
Nodes (26): InvoiceA2AClient, MusicA2AClient, PlannerAgent Instruction Builders, PlannerAgent Intent Detection Helpers, PlannerAgent.invoke, PlannerAgent._invoke_deterministic, PlannerAgent Missing Field Detection, route_after_invoice() (+18 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (10): AgentExecutor, MCPToolAgent.call_tool, MCPToolAgent, MCPToolAgent._parse_text_result, MCPToolAgent._unwrap_mcp_result, MultiServerMCPClient, InvoiceAgent, InvoiceRequest (+2 more)

### Community 5 - "Community 5"
Cohesion: 0.14
Nodes (23): ask_for_missing_info(), _extract_labeled_music_field(), _extract_labeled_value(), extract_missing_fields(), _extract_number(), interrupt_for_missing_info(), test_ask_for_missing_artist(), test_ask_for_missing_genre() (+15 more)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (6): A2AClientError, BaseA2AClient, InvoiceA2AClient, MusicA2AClient, BaseA2AClient, main()

### Community 7 - "Community 7"
Cohesion: 0.14
Nodes (5): MCPToolAgent, MusicAgent, MusicRequest, MusicAgentExecutor, MusicAgentResponse

### Community 8 - "Community 8"
Cohesion: 0.11
Nodes (16): load_agent_card(), Registered A2A Agent Identifiers, get_llm(), Model Provider Settings, a2a AgentExecutor, A2A DefaultRequestHandler, FastAPI Application, MusicAgent (+8 more)

### Community 9 - "Community 9"
Cohesion: 0.19
Nodes (13): AggregatorAgent, AggregatorAgent._format_structured_result, AggregatorAgent.invoke, AggregatorAgent._try_parse_json, AgentResult, AggregatorInput, AggregatorOutput, BaseModel (+5 more)

### Community 10 - "Community 10"
Cohesion: 0.26
Nodes (17): Chinook Invoice Tables, Chinook Music Tables, FastMCP, SQLDatabase, get_employee_by_invoice_and_customer, get_invoices_by_customer_sorted_by_date, get_invoices_sorted_by_unit_price, register_invoice_tools (+9 more)

### Community 11 - "Community 11"
Cohesion: 0.2
Nodes (7): get_db(), create_mcp_server(), main(), main(), test_mcp_database_can_query_latest_invoice_for_customer(), register_invoice_tools(), register_music_tools()

### Community 12 - "Community 12"
Cohesion: 0.2
Nodes (3): main(), run_case(), test_route_after_missing_info_goes_to_music()

### Community 13 - "Community 13"
Cohesion: 0.18
Nodes (10): code:bash (multi-agent-system/), code:bash (uv run python scripts/run_mcp_server.py --host localhost --p), code:bash (uv run python scripts/run_invoice_a2a.py --host localhost --), code:bash (uv run python scripts/run_music_a2a.py --host localhost --po), code:bash (uv run pytest tests -q), code:bash (uv run python scripts/run_planner.py), langgraph-agent, Project Structure (+2 more)

### Community 14 - "Community 14"
Cohesion: 0.28
Nodes (9): PlannerAgent, PlannerAgent.debug_raw_llm, PlannerAgent._invoke_llm, PlannerAgent._normalize_output, PlannerAgent._validate_llm_output, PLANNER_SYSTEM_PROMPT, PlannedTask, PlannerOutput (+1 more)

### Community 17 - "Community 17"
Cohesion: 0.83
Nodes (3): create_thread_config(), get_interrupt_question(), main()

## Ambiguous Edges - Review These
- `LLM` → `Planner CLI Main Loop`  [AMBIGUOUS]
  PROJECT.md · relation: conceptually_related_to

## Knowledge Gaps
- **57 isolated node(s):** `Shared constants used across the orchestration system.`, `Overview`, `Invoice Agent`, `Music Agent`, `Planner Agent` (+52 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `LLM` and `Planner CLI Main Loop`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `final_response_node()` connect `Community 9` to `Community 3`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Why does `PlannerAgent` connect `Community 0` to `Community 8`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `PlannerAgent` (e.g. with `PlannedTask` and `PlannerOutput`) actually correct?**
  _`PlannerAgent` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MusicAgent` (e.g. with `MCPToolAgent` and `MusicAgentResponse`) actually correct?**
  _`MusicAgent` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `extract_missing_fields()` (e.g. with `test_extract_song_title_from_plain_answer()` and `test_extract_artist_from_plain_answer()`) actually correct?**
  _`extract_missing_fields()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `PlannerOutput` (e.g. with `PlannerAgent` and `test_normalize_output_adds_task_id_and_sets_status()`) actually correct?**
  _`PlannerOutput` has 14 INFERRED edges - model-reasoned connections that need verification._