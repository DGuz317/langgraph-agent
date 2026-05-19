# Graph Report - langgraph-agent  (2026-05-19)

## Corpus Check
- 91 files · ~20,251 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 787 nodes · 1267 edges · 67 communities (60 shown, 7 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 254 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dd3c3b60`
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
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]

## God Nodes (most connected - your core abstractions)
1. `PlannerAgent` - 43 edges
2. `MusicAgent` - 30 edges
3. `PlannedTask` - 23 edges
4. `PlannerOutput` - 23 edges
5. `extract_missing_fields()` - 20 edges
6. `MCPToolAgent` - 20 edges
7. `Multi-Agent System Using LangGraph` - 18 edges
8. `_call_tool()` - 17 edges
9. `invoice_node()` - 16 edges
10. `music_node()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `A2A Response Text Extraction` --implements--> `A2A Protocol`  [INFERRED]
  src/multi_agent_system/a2a_client/base.py → PROJECT.md
- `LLM` --conceptually_related_to--> `Planner CLI Main Loop`  [AMBIGUOUS]
  PROJECT.md → scripts/run_planner.py
- `test_llm_planner_returns_structured_tasks_for_core_cases()` --calls--> `PlannerAgent`  [INFERRED]
  tests/test_llm_planner.py → src/multi_agent_system/planner/agent.py
- `test_llm_planner_marks_generic_music_recommendation_as_ambiguous()` --calls--> `PlannerAgent`  [INFERRED]
  tests/test_llm_planner.py → src/multi_agent_system/planner/agent.py
- `test_route_after_missing_info_goes_to_music()` --calls--> `route_after_planner()`  [INFERRED]
  tests/test_planner_graph.py → src/multi_agent_system/planner_app/edges.py

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

## Communities (67 total, 7 thin omitted)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (45): A2A Protocol, Agent Cards, Aggregator Agent, Project Configuration, Human-in-the-Loop, Invoice Agent, LangGraph, LLM (+37 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (18): A2A Clients, A2A Services, Agent Cards, Architecture Overview, code:bash (multi-agent-system/), code:python (import json), code:python (import click), code:json ({) (+10 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (43): AgentResult, AggregatorAgent, InvoiceA2AClient, MusicA2AClient, PlannerAgent Instruction Builders, PlannerAgent Intent Detection Helpers, PlannerAgent.invoke, PlannerAgent._invoke_deterministic (+35 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (22): load_agent_card(), Registered A2A Agent Identifiers, a2a AgentExecutor, A2A DefaultRequestHandler, FastAPI Application, MusicAgent, InvoiceAgent, InvoiceRequest (+14 more)

### Community 5 - "Community 5"
Cohesion: 0.13
Nodes (25): ask_for_missing_info(), _extract_labeled_music_field(), _extract_labeled_value(), extract_missing_fields(), _extract_number(), interrupt_for_missing_info(), test_ask_for_missing_artist(), test_ask_for_missing_genre() (+17 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (16): A2AClientError, BaseA2AClient, InvoiceA2AClient, MusicA2AClient, BaseA2AClient, A2AClientError, Raised when an A2A service request fails., StubA2AClient (+8 more)

### Community 7 - "Community 7"
Cohesion: 0.10
Nodes (10): AgentExecutor, MusicAgent, MusicRequest, MusicAgentExecutor, MusicAgentResponse, test_music_agent_missing_artist_fails_validation(), test_music_agent_parses_artist_requests(), test_music_agent_parses_genre_requests() (+2 more)

### Community 9 - "Community 9"
Cohesion: 0.14
Nodes (20): AggregatorAgent, AggregatorAgent._format_structured_result, AggregatorAgent.invoke, AggregatorAgent._try_parse_json, AgentResult, AggregatorInput, AggregatorOutput, BaseModel (+12 more)

### Community 10 - "Community 10"
Cohesion: 0.26
Nodes (17): Chinook Invoice Tables, Chinook Music Tables, FastMCP, SQLDatabase, get_employee_by_invoice_and_customer, get_invoices_by_customer_sorted_by_date, get_invoices_sorted_by_unit_price, register_invoice_tools (+9 more)

### Community 11 - "Community 11"
Cohesion: 0.10
Nodes (34): get_db(), create_mcp_server(), main(), _assert_non_empty_list_of_dicts(), _call_tool(), _call_tool_async(), db(), _extract_tool_data() (+26 more)

### Community 12 - "Community 12"
Cohesion: 0.18
Nodes (3): main(), run_case(), test_route_after_missing_info_goes_to_music()

### Community 13 - "Community 13"
Cohesion: 0.05
Nodes (52): 1. Start MCP server, 2. Start Invoice A2A service, 3. Start Music A2A service, 4. Run Planner CLI, 5. Or run Planner API, A2A integration test fails with connection error, Architecture, code:text (User query) (+44 more)

### Community 14 - "Community 14"
Cohesion: 0.10
Nodes (21): MCPToolError, MultiAgentSystemError, Raised when an MCP tool call fails., Base error for application-level failures., MCPToolAgent.call_tool, MCPToolAgent, MCPToolAgent._parse_text_result, Base class for agents that call tools exposed by the MCP server. (+13 more)

### Community 17 - "Community 17"
Cohesion: 0.16
Nodes (14): build_async_checkpointer_context(), build_memory_checkpointer(), Checkpointer factory for the planner LangGraph app., Build an in-memory checkpointer for tests and simple local runs., Build the configured checkpointer.      Supported backends:     - memory: volati, create_thread_config(), get_interrupt_question(), main() (+6 more)

### Community 21 - "Community 21"
Cohesion: 0.29
Nodes (7): Architecture Notes, Commands, Graphify, Repository Instructions, Runtime Flow, Stack And Setup, Workflow

### Community 28 - "Community 28"
Cohesion: 0.10
Nodes (16): get_llm(), Model Provider Settings, _get_next_task_for_agent(), _has_arg_value(), _instruction_must_not_be_blank(), _validate_agent_intent_and_required_fields(), _validate_output_consistency(), PlannerAgent (+8 more)

### Community 47 - "Community 47"
Cohesion: 0.08
Nodes (30): PlannerInvokeRequest, PlannerServiceResponse, API request for invoking or resuming the planner., User-facing response returned by PlannerService., _user_input_must_not_be_blank(), create_app(), PlannerServiceProtocol, _extract_final_answer() (+22 more)

### Community 48 - "Community 48"
Cohesion: 0.24
Nodes (13): FakePlanner, FakePlannerOutput, _invoke_graph(), _set_planner_output(), _task(), test_planner_e2e_ambiguous_music_can_choose_artist_after_hitl(), test_planner_e2e_ambiguous_music_defaults_to_genre_after_hitl(), test_planner_e2e_direct_invoice_query_uses_args_first_instruction() (+5 more)

### Community 49 - "Community 49"
Cohesion: 0.17
Nodes (19): PlannedTask, PlannerOutput, RecordingPlanner, test_missing_info_node_preserves_album_intent_when_artist_is_supplied(), test_missing_info_node_replans_with_customer_id(), test_missing_info_node_replans_with_song_title(), test_planned_task_accepts_clarify_music_search_with_missing_search_type(), test_planned_task_accepts_complete_invoice_task() (+11 more)

### Community 50 - "Community 50"
Cohesion: 0.14
Nodes (14): code:python (def build_a2a_payload_from_task(task: dict) -> dict:), code:text (A2A receives instruction text), code:text (A2A receives intent + args as structured payload), code:text (Recommend songs by genre Jazz), code:json ({), code:text (invoice → music → final_response), code:text (invoice ┐), Future Roadmap (+6 more)

### Community 51 - "Community 51"
Cohesion: 0.25
Nodes (12): build_instruction_from_task(), Raised when a planner task cannot be converted into an executable instruction., _require_arg(), TaskInstructionError, test_build_albums_by_artist_instruction(), test_build_check_song_instruction(), test_build_invoices_by_unit_price_instruction(), test_build_latest_invoice_instruction() (+4 more)

### Community 52 - "Community 52"
Cohesion: 0.20
Nodes (10): FakeEmptyLLM, FakeEmptyStructuredLLM, FakeLLM, FakeStructuredLLM, test_normalize_output_adds_task_id_and_sets_status(), test_normalize_output_preserves_task_args(), test_planner_agent_allows_llm_to_return_no_tasks(), test_planner_agent_invokes_structured_llm() (+2 more)

### Community 53 - "Community 53"
Cohesion: 0.21
Nodes (12): code:text (src/multi_agent_system/orchestrator/server.py), code:http (POST /planner/invoke), code:json ({), code:json ({), code:bash (uv run python scripts/run_mcp_server.py --host localhost --p), code:bash (uv run python scripts/run_invoice_a2a.py --host localhost --), code:bash (uv run python scripts/run_music_a2a.py --host localhost --po), code:bash (uv run python tests/test_planner_graph.py) (+4 more)

### Community 54 - "Community 54"
Cohesion: 0.18
Nodes (10): capabilities, pushNotifications, streaming, defaultInputModes, defaultOutputModes, description, name, skills (+2 more)

### Community 55 - "Community 55"
Cohesion: 0.18
Nodes (10): capabilities, pushNotifications, streaming, defaultInputModes, defaultOutputModes, description, name, skills (+2 more)

### Community 56 - "Community 56"
Cohesion: 0.28
Nodes (9): PlannerAgent, PlannerAgent.debug_raw_llm, PlannerAgent._invoke_llm, PlannerAgent._normalize_output, PlannerAgent._validate_llm_output, PLANNER_SYSTEM_PROMPT, PlannedTask, PlannerOutput (+1 more)

### Community 57 - "Community 57"
Cohesion: 0.39
Nodes (7): make_client(), test_send_message_raises_on_connection_error(), test_send_message_raises_on_http_500(), test_send_message_raises_on_invalid_json(), test_send_message_raises_on_jsonrpc_error(), test_send_message_raises_on_timeout(), test_send_message_returns_jsonrpc_body()

### Community 58 - "Community 58"
Cohesion: 0.33
Nodes (6): Agents:, Aggregator Agent, Invoice Agent, Key Components:, Music Agent, Planner Agent

### Community 59 - "Community 59"
Cohesion: 0.40
Nodes (5): main(), run_case(), test_llm_planner_accepts_hitl_context_for_replanning(), test_llm_planner_marks_generic_music_recommendation_as_ambiguous(), test_llm_planner_returns_structured_tasks_for_core_cases()

### Community 60 - "Community 60"
Cohesion: 0.50
Nodes (4): code:text (User input), Completed Reliability Work, Current Execution Flow, Current Reliability Improvements

### Community 61 - "Community 61"
Cohesion: 0.50
Nodes (4): code:python (from pydantic_settings import BaseSettings), code:python (MODEL_PROVIDER=ollama), config.py, Configuration

### Community 63 - "Community 63"
Cohesion: 0.67
Nodes (3): code:python (from langchain_community.utilities import SQLDatabase), code:bash (uv run python scripts/run_mcp_server.py --host localhost --p), MCP Server

## Ambiguous Edges - Review These
- `LLM` → `Planner CLI Main Loop`  [AMBIGUOUS]
  PROJECT.md · relation: conceptually_related_to

## Knowledge Gaps
- **99 isolated node(s):** `PreToolUse`, `name`, `description`, `supportedInterfaces`, `version` (+94 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `LLM` and `Planner CLI Main Loop`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `PlannerAgent` connect `Community 0` to `Community 49`, `Community 59`, `Community 28`, `Community 52`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `build_graph()` connect `Community 3` to `Community 17`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `main()` connect `Community 17` to `Community 3`, `Community 14`, `Community 47`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `PlannerAgent` (e.g. with `test_normalize_output_adds_task_id_and_sets_status()` and `test_llm_planner_returns_structured_tasks_for_core_cases()`) actually correct?**
  _`PlannerAgent` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `MusicAgent` (e.g. with `MCPToolAgent` and `test_music_agent_parses_artist_requests()`) actually correct?**
  _`MusicAgent` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `PlannedTask` (e.g. with `test_normalize_output_adds_task_id_and_sets_status()` and `test_normalize_output_preserves_task_args()`) actually correct?**
  _`PlannedTask` has 21 INFERRED edges - model-reasoned connections that need verification._