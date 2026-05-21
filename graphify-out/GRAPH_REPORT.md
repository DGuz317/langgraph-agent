# Graph Report - .  (2026-05-21)

## Corpus Check
- Corpus is ~21,414 words - fits in a single context window. You may not need a graph.

## Summary
- 558 nodes · 873 edges · 58 communities (50 shown, 8 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 187 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Planner API Service|Planner API Service]]
- [[_COMMUNITY_A2A Client Layer|A2A Client Layer]]
- [[_COMMUNITY_MCP Server Tools|MCP Server Tools]]
- [[_COMMUNITY_MCP Tool Agent|MCP Tool Agent]]
- [[_COMMUNITY_Invoice Domain Agent|Invoice Domain Agent]]
- [[_COMMUNITY_Architecture Documentation|Architecture Documentation]]
- [[_COMMUNITY_Music Domain Agent|Music Domain Agent]]
- [[_COMMUNITY_LangGraph Nodes|LangGraph Nodes]]
- [[_COMMUNITY_Task Instructions|Task Instructions]]
- [[_COMMUNITY_Result Aggregation|Result Aggregation]]
- [[_COMMUNITY_Planner Validation|Planner Validation]]
- [[_COMMUNITY_Planner Schemas|Planner Schemas]]
- [[_COMMUNITY_End To End Flows|End To End Flows]]
- [[_COMMUNITY_Human In The Loop|Human In The Loop]]
- [[_COMMUNITY_A2A Executors|A2A Executors]]
- [[_COMMUNITY_Graph Checkpointing|Graph Checkpointing]]
- [[_COMMUNITY_LLM Planner|LLM Planner]]
- [[_COMMUNITY_Invoice Agent Card|Invoice Agent Card]]
- [[_COMMUNITY_Music Agent Card|Music Agent Card]]
- [[_COMMUNITY_Graph Routing Tests|Graph Routing Tests]]
- [[_COMMUNITY_A2A Error Handling|A2A Error Handling]]
- [[_COMMUNITY_Tool Hooks|Tool Hooks]]
- [[_COMMUNITY_Runtime Settings|Runtime Settings]]
- [[_COMMUNITY_Planner App State|Planner App State]]
- [[_COMMUNITY_Shared Constants|Shared Constants]]
- [[_COMMUNITY_Sequential Execution Rationale|Sequential Execution Rationale]]
- [[_COMMUNITY_Repository Guidance|Repository Guidance]]

## God Nodes (most connected - your core abstractions)
1. `MusicAgent` - 26 edges
2. `InvoiceAgent` - 21 edges
3. `MCPToolAgent` - 18 edges
4. `_call_tool()` - 17 edges
5. `PlannerService` - 16 edges
6. `invoice_node()` - 15 edges
7. `build_instruction_from_task()` - 14 edges
8. `PlannedTask` - 14 edges
9. `FakeClient` - 13 edges
10. `StubA2AClient` - 13 edges

## Surprising Connections (you probably didn't know these)
- `HITL Owns Missing Information Collection` --semantically_similar_to--> `Thread ID Preservation`  [INFERRED] [semantically similar]
  README.md → AGENTS.md
- `test_build_latest_invoice_instruction()` --calls--> `build_instruction_from_task()`  [INFERRED]
  tests/test_task_instructions.py → src/multi_agent_system/planner_app/task_instructions.py
- `test_build_a2a_payload_from_invoice_task()` --calls--> `build_a2a_payload_from_task()`  [INFERRED]
  tests/test_task_instructions.py → src/multi_agent_system/planner_app/task_instructions.py
- `test_build_all_invoices_instruction()` --calls--> `build_instruction_from_task()`  [INFERRED]
  tests/test_task_instructions.py → src/multi_agent_system/planner_app/task_instructions.py
- `test_build_a2a_payload_from_all_invoices_task()` --calls--> `build_a2a_payload_from_task()`  [INFERRED]
  tests/test_task_instructions.py → src/multi_agent_system/planner_app/task_instructions.py

## Hyperedges (group relationships)
- **Runtime Request Flow** — readme_user_query, readme_planner_langgraph_app, readme_llm_planner_agent, readme_task_routing, readme_aggregator_agent, readme_final_answer [EXTRACTED 1.00]
- **Invoice Data Path** — readme_invoice_a2a_client, readme_invoice_a2a_service, readme_invoice_mcp_tools, readme_chinook_db [EXTRACTED 1.00]
- **Music Data Path** — readme_music_a2a_client, readme_music_a2a_service, readme_music_mcp_tools, readme_chinook_db [EXTRACTED 1.00]

## Communities (58 total, 8 thin omitted)

### Community 0 - "Planner API Service"
Cohesion: 0.08
Nodes (30): PlannerInvokeRequest, PlannerServiceResponse, API request for invoking or resuming the planner., User-facing response returned by PlannerService., _user_input_must_not_be_blank(), create_app(), PlannerServiceProtocol, _extract_final_answer() (+22 more)

### Community 1 - "A2A Client Layer"
Cohesion: 0.07
Nodes (18): BaseA2AClient, InvoiceA2AClient, MusicA2AClient, BaseA2AClient, A2AClientError, Raised when an A2A service request fails., StubA2AClient, test_ask_combines_multiple_text_parts() (+10 more)

### Community 2 - "MCP Server Tools"
Cohesion: 0.10
Nodes (32): get_db(), create_mcp_server(), main(), _assert_non_empty_list_of_dicts(), _call_tool(), _call_tool_async(), db(), _extract_tool_data() (+24 more)

### Community 3 - "MCP Tool Agent"
Cohesion: 0.12
Nodes (17): MCPToolError, MultiAgentSystemError, Raised when an MCP tool call fails., Base error for application-level failures., MCPToolAgent, Base class for agents that call tools exposed by the MCP server., RuntimeError, FakeClient (+9 more)

### Community 4 - "Invoice Domain Agent"
Cohesion: 0.11
Nodes (8): BaseModel, InvoiceAgent, InvoiceRequest, InvoiceAgentResponse, MCPToolAgent, test_invoice_agent_does_not_treat_invoice_id_as_customer_id(), test_invoice_agent_missing_customer_id_fails_validation(), test_invoice_agent_parse_request()

### Community 5 - "Architecture Documentation"
Cohesion: 0.09
Nodes (29): Runtime Config, Service Start Order, Thread ID Preservation, A2A, Aggregator Agent, Aggregator Formats Results, Chinook SQLite Database, Domain Agents Stay Focused (+21 more)

### Community 6 - "Music Domain Agent"
Cohesion: 0.13
Nodes (8): MusicAgent, MusicRequest, MusicAgentResponse, test_music_agent_missing_artist_fails_validation(), test_music_agent_parses_artist_requests(), test_music_agent_parses_genre_requests(), test_music_agent_parses_song_check_requests(), test_song_title_with_genre_word_does_not_become_genre_request()

### Community 7 - "LangGraph Nodes"
Cohesion: 0.15
Nodes (21): _attach_a2a_payload(), _copy_planner_output(), _failure_result(), _get_next_task_for_agent(), invoice_node(), _mark_task_failed(), missing_info_node(), music_node() (+13 more)

### Community 8 - "Task Instructions"
Cohesion: 0.16
Nodes (23): build_a2a_payload_from_task(), build_instruction_from_task(), Raised when a planner task cannot be converted into an executable instruction., _require_arg(), _require_task_field(), TaskInstructionError, test_build_a2a_payload_copies_args(), test_build_a2a_payload_from_all_invoices_task() (+15 more)

### Community 9 - "Result Aggregation"
Cohesion: 0.17
Nodes (15): AggregatorAgent, AgentResult, AggregatorInput, AggregatorOutput, final_response_node(), aggregate(), test_aggregator_combines_multiple_agent_results_in_order(), test_aggregator_formats_dict_result_without_data() (+7 more)

### Community 10 - "Planner Validation"
Cohesion: 0.13
Nodes (13): _has_arg_value(), _instruction_must_not_be_blank(), _validate_agent_intent_and_required_fields(), _validate_output_consistency(), PlannerAgent, FailingPlannerAgent, RepairablePlannerAgent, test_planner_repairs_generic_music_request_to_clarify_search() (+5 more)

### Community 11 - "Planner Schemas"
Cohesion: 0.17
Nodes (19): PlannedTask, PlannerOutput, test_normalize_output_adds_task_id_and_sets_status(), test_normalize_output_preserves_task_args(), test_planned_task_accepts_all_invoices_task(), test_planned_task_accepts_clarify_music_search_with_missing_search_type(), test_planned_task_accepts_complete_invoice_task(), test_planned_task_accepts_latest_invoice_support_employee_task() (+11 more)

### Community 12 - "End To End Flows"
Cohesion: 0.25
Nodes (15): FakePlanner, FakePlannerOutput, _invoke_graph(), _set_planner_output(), _task(), test_planner_e2e_all_invoices_query_uses_args_first_instruction(), test_planner_e2e_ambiguous_music_can_choose_artist_after_hitl(), test_planner_e2e_ambiguous_music_defaults_to_genre_after_hitl() (+7 more)

### Community 13 - "Human In The Loop"
Cohesion: 0.18
Nodes (18): ask_for_missing_info(), _extract_labeled_value(), extract_missing_fields(), interrupt_for_missing_info(), test_ask_for_missing_artist(), test_ask_for_missing_genre(), test_ask_for_missing_music_search_type(), test_ask_for_missing_song_title() (+10 more)

### Community 14 - "A2A Executors"
Cohesion: 0.12
Nodes (8): AgentExecutor, load_agent_card(), InvoiceAgentExecutor, create_app(), main(), MusicAgentExecutor, create_app(), main()

### Community 15 - "Graph Checkpointing"
Cohesion: 0.14
Nodes (13): build_async_checkpointer_context(), build_memory_checkpointer(), Checkpointer factory for the planner LangGraph app., Build an in-memory checkpointer for tests and simple local runs., Build the configured checkpointer.      Supported backends:     - memory: volati, build_graph(), main(), test_async_checkpointer_context_is_case_insensitive() (+5 more)

### Community 17 - "Invoice Agent Card"
Cohesion: 0.18
Nodes (10): capabilities, pushNotifications, streaming, defaultInputModes, defaultOutputModes, description, name, skills (+2 more)

### Community 18 - "Music Agent Card"
Cohesion: 0.18
Nodes (10): capabilities, pushNotifications, streaming, defaultInputModes, defaultOutputModes, description, name, skills (+2 more)

### Community 20 - "A2A Error Handling"
Cohesion: 0.39
Nodes (7): make_client(), test_send_message_raises_on_connection_error(), test_send_message_raises_on_http_500(), test_send_message_raises_on_invalid_json(), test_send_message_raises_on_jsonrpc_error(), test_send_message_raises_on_timeout(), test_send_message_returns_jsonrpc_body()

## Knowledge Gaps
- **20 isolated node(s):** `PreToolUse`, `name`, `description`, `supportedInterfaces`, `version` (+15 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MCPToolAgent` connect `MCP Tool Agent` to `Invoice Domain Agent`, `Music Domain Agent`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `build_async_checkpointer_context()` connect `Graph Checkpointing` to `Planner Validation`, `MCP Tool Agent`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `final_response_node()` connect `Result Aggregation` to `LangGraph Nodes`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `MusicAgent` (e.g. with `MCPToolAgent` and `test_music_agent_parses_artist_requests()`) actually correct?**
  _`MusicAgent` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `InvoiceAgent` (e.g. with `MCPToolAgent` and `test_invoice_agent_parse_request()`) actually correct?**
  _`InvoiceAgent` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `MCPToolAgent` (e.g. with `FakeTool` and `FakeClient`) actually correct?**
  _`MCPToolAgent` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `PlannerService` (e.g. with `FakeGraph` and `FakeInterrupt`) actually correct?**
  _`PlannerService` has 12 INFERRED edges - model-reasoned connections that need verification._