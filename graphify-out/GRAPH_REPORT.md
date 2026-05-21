# Graph Report - .  (2026-05-21)

## Corpus Check
- Corpus is ~21,414 words - fits in a single context window. You may not need a graph.

## Summary
- 583 nodes · 900 edges · 58 communities (52 shown, 6 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 187 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Planner API Service|Planner API Service]]
- [[_COMMUNITY_A2A Client Layer|A2A Client Layer]]
- [[_COMMUNITY_Runtime Architecture|Runtime Architecture]]
- [[_COMMUNITY_MCP Data Tools|MCP Data Tools]]
- [[_COMMUNITY_MCP Tool Client|MCP Tool Client]]
- [[_COMMUNITY_Planner Agent Logic|Planner Agent Logic]]
- [[_COMMUNITY_Invoice Domain Agent|Invoice Domain Agent]]
- [[_COMMUNITY_Music Domain Agent|Music Domain Agent]]
- [[_COMMUNITY_Graph Execution Nodes|Graph Execution Nodes]]
- [[_COMMUNITY_Planner Validation|Planner Validation]]
- [[_COMMUNITY_Final Aggregation|Final Aggregation]]
- [[_COMMUNITY_Task Instruction Builder|Task Instruction Builder]]
- [[_COMMUNITY_Graph Test Fixtures|Graph Test Fixtures]]
- [[_COMMUNITY_Human In The Loop|Human In The Loop]]
- [[_COMMUNITY_A2A Agent Executors|A2A Agent Executors]]
- [[_COMMUNITY_Planner Checkpointing|Planner Checkpointing]]
- [[_COMMUNITY_Graphify Detection Data|Graphify Detection Data]]
- [[_COMMUNITY_Invoice Agent Card|Invoice Agent Card]]
- [[_COMMUNITY_Music Agent Card|Music Agent Card]]
- [[_COMMUNITY_Planner Routing Tests|Planner Routing Tests]]
- [[_COMMUNITY_A2A Error Tests|A2A Error Tests]]
- [[_COMMUNITY_Repository Workflow|Repository Workflow]]
- [[_COMMUNITY_Runtime Settings|Runtime Settings]]
- [[_COMMUNITY_Tool Hooks|Tool Hooks]]
- [[_COMMUNITY_Planner App State|Planner App State]]
- [[_COMMUNITY_Shared Constants|Shared Constants]]
- [[_COMMUNITY_Git Workflow|Git Workflow]]

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
- `Sequential Debuggable Workflow` --semantically_similar_to--> `Parallel Multi-Agent Execution`  [INFERRED] [semantically similar]
  README.md → PROJECT.md
- `Design Principles` --semantically_similar_to--> `Domain Boundary Rule`  [INFERRED] [semantically similar]
  README.md → AGENTS.md
- `test_build_latest_invoice_instruction()` --calls--> `build_instruction_from_task()`  [INFERRED]
  tests/test_task_instructions.py → src/multi_agent_system/planner_app/task_instructions.py
- `test_build_a2a_payload_from_invoice_task()` --calls--> `build_a2a_payload_from_task()`  [INFERRED]
  tests/test_task_instructions.py → src/multi_agent_system/planner_app/task_instructions.py
- `test_build_all_invoices_instruction()` --calls--> `build_instruction_from_task()`  [INFERRED]
  tests/test_task_instructions.py → src/multi_agent_system/planner_app/task_instructions.py

## Hyperedges (group relationships)
- **Runtime Architecture Flow** — readme_planner_langgraph_app, readme_llm_planner_agent, readme_human_in_the_loop_interrupts, readme_task_routing, readme_invoice_a2a_client, readme_music_a2a_client, project_invoice_a2a_service, project_music_a2a_service, readme_invoice_mcp_tools, readme_music_mcp_tools, readme_chinook_db, readme_aggregator_agent [EXTRACTED 1.00]
- **Structured Payload Compatibility Pattern** — project_task_args_source_of_truth, project_build_a2a_payload_from_task, project_text_compatible_a2a_instruction, project_structured_a2a_payload_contract [EXTRACTED 1.00]
- **Component Boundary Principles** — readme_design_principles, readme_domain_agents_stay_focused, readme_mcp_tools_only_access_data, project_aggregator, project_task_args_source_of_truth [EXTRACTED 1.00]

## Communities (58 total, 6 thin omitted)

### Community 0 - "Planner API Service"
Cohesion: 0.08
Nodes (30): PlannerInvokeRequest, PlannerServiceResponse, API request for invoking or resuming the planner., User-facing response returned by PlannerService., _user_input_must_not_be_blank(), create_app(), PlannerServiceProtocol, _extract_final_answer() (+22 more)

### Community 1 - "A2A Client Layer"
Cohesion: 0.07
Nodes (18): BaseA2AClient, InvoiceA2AClient, MusicA2AClient, BaseA2AClient, A2AClientError, Raised when an A2A service request fails., StubA2AClient, test_ask_combines_multiple_text_parts() (+10 more)

### Community 2 - "Runtime Architecture"
Cohesion: 0.07
Nodes (38): Domain Boundary Rule, Planner Output Structured Schema, Service Start Order, Thread ID Resume Behavior, A2A Services, Aggregator, build_a2a_payload_from_task, Chinook SQLite Database (+30 more)

### Community 3 - "MCP Data Tools"
Cohesion: 0.10
Nodes (32): get_db(), create_mcp_server(), main(), _assert_non_empty_list_of_dicts(), _call_tool(), _call_tool_async(), db(), _extract_tool_data() (+24 more)

### Community 4 - "MCP Tool Client"
Cohesion: 0.12
Nodes (17): MCPToolError, MultiAgentSystemError, Raised when an MCP tool call fails., Base error for application-level failures., MCPToolAgent, Base class for agents that call tools exposed by the MCP server., RuntimeError, FakeClient (+9 more)

### Community 5 - "Planner Agent Logic"
Cohesion: 0.11
Nodes (20): PlannerAgent, PlannedTask, PlannerOutput, test_normalize_output_adds_task_id_and_sets_status(), test_normalize_output_preserves_task_args(), test_planned_task_accepts_all_invoices_task(), test_planned_task_accepts_clarify_music_search_with_missing_search_type(), test_planned_task_accepts_complete_invoice_task() (+12 more)

### Community 6 - "Invoice Domain Agent"
Cohesion: 0.11
Nodes (7): InvoiceAgent, InvoiceRequest, InvoiceAgentResponse, MCPToolAgent, test_invoice_agent_does_not_treat_invoice_id_as_customer_id(), test_invoice_agent_missing_customer_id_fails_validation(), test_invoice_agent_parse_request()

### Community 7 - "Music Domain Agent"
Cohesion: 0.13
Nodes (8): MusicAgent, MusicRequest, MusicAgentResponse, test_music_agent_missing_artist_fails_validation(), test_music_agent_parses_artist_requests(), test_music_agent_parses_genre_requests(), test_music_agent_parses_song_check_requests(), test_song_title_with_genre_word_does_not_become_genre_request()

### Community 8 - "Graph Execution Nodes"
Cohesion: 0.15
Nodes (21): _attach_a2a_payload(), _copy_planner_output(), _failure_result(), _get_next_task_for_agent(), invoice_node(), _mark_task_failed(), missing_info_node(), music_node() (+13 more)

### Community 9 - "Planner Validation"
Cohesion: 0.11
Nodes (14): get_llm(), _has_arg_value(), _instruction_must_not_be_blank(), _validate_agent_intent_and_required_fields(), _validate_output_consistency(), PlannerAgent, FailingPlannerAgent, RepairablePlannerAgent (+6 more)

### Community 10 - "Final Aggregation"
Cohesion: 0.17
Nodes (16): AggregatorAgent, AgentResult, AggregatorInput, AggregatorOutput, BaseModel, final_response_node(), aggregate(), test_aggregator_combines_multiple_agent_results_in_order() (+8 more)

### Community 11 - "Task Instruction Builder"
Cohesion: 0.16
Nodes (23): build_a2a_payload_from_task(), build_instruction_from_task(), Raised when a planner task cannot be converted into an executable instruction., _require_arg(), _require_task_field(), TaskInstructionError, test_build_a2a_payload_copies_args(), test_build_a2a_payload_from_all_invoices_task() (+15 more)

### Community 12 - "Graph Test Fixtures"
Cohesion: 0.25
Nodes (15): FakePlanner, FakePlannerOutput, _invoke_graph(), _set_planner_output(), _task(), test_planner_e2e_all_invoices_query_uses_args_first_instruction(), test_planner_e2e_ambiguous_music_can_choose_artist_after_hitl(), test_planner_e2e_ambiguous_music_defaults_to_genre_after_hitl() (+7 more)

### Community 13 - "Human In The Loop"
Cohesion: 0.18
Nodes (18): ask_for_missing_info(), _extract_labeled_value(), extract_missing_fields(), interrupt_for_missing_info(), test_ask_for_missing_artist(), test_ask_for_missing_genre(), test_ask_for_missing_music_search_type(), test_ask_for_missing_song_title() (+10 more)

### Community 14 - "A2A Agent Executors"
Cohesion: 0.12
Nodes (8): AgentExecutor, load_agent_card(), InvoiceAgentExecutor, create_app(), main(), MusicAgentExecutor, create_app(), main()

### Community 15 - "Planner Checkpointing"
Cohesion: 0.14
Nodes (13): build_async_checkpointer_context(), build_memory_checkpointer(), Checkpointer factory for the planner LangGraph app., Build an in-memory checkpointer for tests and simple local runs., Build the configured checkpointer.      Supported backends:     - memory: volati, build_graph(), main(), test_async_checkpointer_context_is_case_insensitive() (+5 more)

### Community 16 - "Graphify Detection Data"
Cohesion: 0.14
Nodes (13): files, code, document, image, paper, video, graphifyignore_patterns, needs_graph (+5 more)

### Community 17 - "Invoice Agent Card"
Cohesion: 0.18
Nodes (10): capabilities, pushNotifications, streaming, defaultInputModes, defaultOutputModes, description, name, skills (+2 more)

### Community 18 - "Music Agent Card"
Cohesion: 0.18
Nodes (10): capabilities, pushNotifications, streaming, defaultInputModes, defaultOutputModes, description, name, skills (+2 more)

### Community 20 - "A2A Error Tests"
Cohesion: 0.39
Nodes (7): make_client(), test_send_message_raises_on_connection_error(), test_send_message_raises_on_http_500(), test_send_message_raises_on_invalid_json(), test_send_message_raises_on_jsonrpc_error(), test_send_message_raises_on_timeout(), test_send_message_returns_jsonrpc_body()

### Community 21 - "Repository Workflow"
Cohesion: 0.50
Nodes (4): Graphify Workflow, Repository Instructions, Runtime Configuration, uv Package Management

## Knowledge Gaps
- **35 isolated node(s):** `code`, `document`, `paper`, `image`, `video` (+30 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MCPToolAgent` connect `MCP Tool Client` to `Invoice Domain Agent`, `Music Domain Agent`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Why does `build_async_checkpointer_context()` connect `Planner Checkpointing` to `Planner Validation`, `MCP Tool Client`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `final_response_node()` connect `Final Aggregation` to `Graph Execution Nodes`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `MusicAgent` (e.g. with `MCPToolAgent` and `test_music_agent_parses_artist_requests()`) actually correct?**
  _`MusicAgent` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `InvoiceAgent` (e.g. with `MCPToolAgent` and `test_invoice_agent_parse_request()`) actually correct?**
  _`InvoiceAgent` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `MCPToolAgent` (e.g. with `FakeTool` and `FakeClient`) actually correct?**
  _`MCPToolAgent` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `PlannerService` (e.g. with `FakeGraph` and `FakeInterrupt`) actually correct?**
  _`PlannerService` has 12 INFERRED edges - model-reasoned connections that need verification._