# Graph Report - .  (2026-05-25)

## Corpus Check
- Corpus is ~21,594 words - fits in a single context window. You may not need a graph.

## Summary
- 686 nodes · 1002 edges · 73 communities (61 shown, 12 thin omitted)
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 256 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_API Service Models|API Service Models]]
- [[_COMMUNITY_Runtime Configuration|Runtime Configuration]]
- [[_COMMUNITY_A2A Client Transport|A2A Client Transport]]
- [[_COMMUNITY_MCP Data Server|MCP Data Server]]
- [[_COMMUNITY_Shared Tool Errors|Shared Tool Errors]]
- [[_COMMUNITY_Planner Agent Logic|Planner Agent Logic]]
- [[_COMMUNITY_Invoice Agent Logic|Invoice Agent Logic]]
- [[_COMMUNITY_Music Agent Tools|Music Agent Tools]]
- [[_COMMUNITY_Planner Execution Nodes|Planner Execution Nodes]]
- [[_COMMUNITY_Planner Schema Validation|Planner Schema Validation]]
- [[_COMMUNITY_Task Instruction Builder|Task Instruction Builder]]
- [[_COMMUNITY_Response Aggregation|Response Aggregation]]
- [[_COMMUNITY_Invoice A2A Executor|Invoice A2A Executor]]
- [[_COMMUNITY_Args-First Contract Tests|Args-First Contract Tests]]
- [[_COMMUNITY_End-to-End Flow Fixtures|End-to-End Flow Fixtures]]
- [[_COMMUNITY_Human Review Logic|Human Review Logic]]
- [[_COMMUNITY_Response Integration|Response Integration]]
- [[_COMMUNITY_Orchestrator Service Flow|Orchestrator Service Flow]]
- [[_COMMUNITY_Checkpoint Management|Checkpoint Management]]
- [[_COMMUNITY_HITL Repair Tests|HITL Repair Tests]]
- [[_COMMUNITY_Invoice Agent Card|Invoice Agent Card]]
- [[_COMMUNITY_Music Agent Card|Music Agent Card]]
- [[_COMMUNITY_Routing Graph Tests|Routing Graph Tests]]
- [[_COMMUNITY_A2A Error Tests|A2A Error Tests]]
- [[_COMMUNITY_Typed A2A API|Typed A2A API]]
- [[_COMMUNITY_Graphify Instructions|Graphify Instructions]]
- [[_COMMUNITY_Architecture Documentation|Architecture Documentation]]
- [[_COMMUNITY_Transport Integration Tests|Transport Integration Tests]]
- [[_COMMUNITY_MCP Tool Surface|MCP Tool Surface]]
- [[_COMMUNITY_JSON-RPC Response Handling|JSON-RPC Response Handling]]
- [[_COMMUNITY_Hook Configuration|Hook Configuration]]
- [[_COMMUNITY_Settings Model|Settings Model]]
- [[_COMMUNITY_Planner State Type|Planner State Type]]
- [[_COMMUNITY_Shared Constants|Shared Constants]]
- [[_COMMUNITY_Music Parsing Priority|Music Parsing Priority]]
- [[_COMMUNITY_Sequential Execution Rationale|Sequential Execution Rationale]]
- [[_COMMUNITY_Base Client Class|Base Client Class]]
- [[_COMMUNITY_Invoice Request Model|Invoice Request Model]]
- [[_COMMUNITY_Invoice Executor Class|Invoice Executor Class]]

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
- `Graphify PreToolUse Hook Check` --implements--> `Graphify Workflow`  [INFERRED]
  .codex/hooks.json → AGENTS.md
- `Design Principles` --semantically_similar_to--> `Domain Boundary Rule`  [INFERRED] [semantically similar]
  README.md → AGENTS.md
- `InvoiceAgent` --implements--> `Invoice Support Employee Enrichment Rule`  [INFERRED]
  src/multi_agent_system/a2a_servers/invoice_agent/agent.py → PROJECT.md
- `test_build_latest_invoice_instruction()` --calls--> `build_instruction_from_task()`  [INFERRED]
  tests/test_task_instructions.py → src/multi_agent_system/planner_app/task_instructions.py
- `test_build_a2a_payload_from_invoice_task()` --calls--> `build_a2a_payload_from_task()`  [INFERRED]
  tests/test_task_instructions.py → src/multi_agent_system/planner_app/task_instructions.py

## Hyperedges (group relationships)
- **Runtime Architecture Flow** — project_planner_service, project_planner_output, project_hitl_interrupt_resume, project_task_args_source_of_truth, project_text_compatible_a2a_instruction, project_invoice_a2a_service, project_music_a2a_service, project_fastmcp_tools, project_chinook_sqlite_database, project_aggregator [EXTRACTED 1.00]
- **A2A Text JSON-RPC Client Flow** — base_jsonrpc_message_contract, base_send_message, base_extract_text_response, invoice_a2a_client, music_a2a_client [EXTRACTED 1.00]
- **Invoice Support Employee Enrichment Flow** — project_invoice_support_employee_rule, invoice_agent_get_all_invoices, invoice_agent_get_latest_with_support, invoice_agent_enrich_invoices, invoice_agent_get_support_for_invoice, invoice_tool_employee_by_invoice_customer [EXTRACTED 1.00]
- **Music Intent To MCP Capability Dispatch** — music_agent_ainvoke, music_agent_get_albums_by_artist, music_agent_get_tracks_by_artist, music_agent_get_songs_by_genre, music_agent_check_song, common_mcp_tool_agent_call_tool [EXTRACTED 1.00]
- **Structured Agent Response Aggregation Contract** — invoice_agent_schemas_InvoiceAgentResponse, music_agent_schemas_MusicAgentResponse, aggregator_schemas_AgentResult, aggregator_agent_format_dict_result [INFERRED 0.90]
- **Database-Backed MCP Tool Surface** — mcp_db_get_db, mcp_server_create_mcp_server, mcp_invoice_register_invoice_tools, mcp_music_register_music_tools [EXTRACTED 1.00]
- **Structured Planning State Handoff** — planner_system_prompt_contract, planner_planned_task, planner_planner_output, planner_planner_agent, planner_app_planner_node, planner_app_state [INFERRED 0.94]
- **Interruptible Planner Execution** — orchestrator_planner_service_invoke, planner_app_build_graph, planner_app_interrupt_for_missing_info, planner_app_missing_info_node, planner_app_state [INFERRED 0.90]
- **Args-First A2A Execution Flow** — task_instructions_args_first_execution_contract, test_node_instruction_rebuild_args_contract, test_a2a_payload_integration_payload_contract, test_planner_e2e_flows_graph_contract [INFERRED 0.90]
- **Threaded HITL Resume Flow** — test_planner_graph_missing_info_contract, test_planner_e2e_flows_graph_contract, test_orchestrator_api_http_contract, test_orchestrator_api_integration_thread_contract [INFERRED 0.88]
- **Invoice Support Employee Enrichment Flow** — test_invoice_agent_parsing_support_enrichment_contract, test_mcp_tools_service_contract, test_invoice_support_employee_integration_contract [INFERRED 0.91]
- **Customer ID HITL Resume Flow** — test_planner_repair_missing_field, test_planner_schema_missing_fields, test_planner_hitl_missing_field_parsing, test_planner_service_interrupt_resume [INFERRED 0.83]
- **Music Clarification Before Execution Flow** — test_planner_repair_music_clarification, test_planner_schema_clarify_music_search, test_planner_hitl_music_search_clarification, test_task_instructions_clarify_non_executable [INFERRED 0.92]
- **Structured Task to A2A Payload Contract** — test_planner_schema_planned_task_validation, test_task_instructions_instruction_builder, test_task_instructions_a2a_payload [INFERRED 0.88]

## Communities (73 total, 12 thin omitted)

### Community 0 - "API Service Models"
Cohesion: 0.08
Nodes (31): BaseModel, PlannerInvokeRequest, PlannerServiceResponse, API request for invoking or resuming the planner., User-facing response returned by PlannerService., _user_input_must_not_be_blank(), create_app(), PlannerServiceProtocol (+23 more)

### Community 1 - "Runtime Configuration"
Cohesion: 0.05
Nodes (36): Domain Boundary Rule, A2A Endpoint Settings, Model Provider Configuration, Settings, SQLITE_DB Configuration, InvoiceA2AClient, InvoiceAgent, InvoiceAgent.ainvoke() (+28 more)

### Community 2 - "A2A Client Transport"
Cohesion: 0.07
Nodes (18): BaseA2AClient, InvoiceA2AClient, MusicA2AClient, BaseA2AClient, A2AClientError, Raised when an A2A service request fails., StubA2AClient, test_ask_combines_multiple_text_parts() (+10 more)

### Community 3 - "MCP Data Server"
Cohesion: 0.10
Nodes (32): get_db(), create_mcp_server(), main(), _assert_non_empty_list_of_dicts(), _call_tool(), _call_tool_async(), db(), _extract_tool_data() (+24 more)

### Community 4 - "Shared Tool Errors"
Cohesion: 0.12
Nodes (17): MCPToolError, MultiAgentSystemError, Raised when an MCP tool call fails., Base error for application-level failures., MCPToolAgent, Base class for agents that call tools exposed by the MCP server., RuntimeError, FakeClient (+9 more)

### Community 5 - "Planner Agent Logic"
Cohesion: 0.11
Nodes (20): PlannerAgent, PlannedTask, PlannerOutput, test_normalize_output_adds_task_id_and_sets_status(), test_normalize_output_preserves_task_args(), test_planned_task_accepts_all_invoices_task(), test_planned_task_accepts_clarify_music_search_with_missing_search_type(), test_planned_task_accepts_complete_invoice_task() (+12 more)

### Community 6 - "Invoice Agent Logic"
Cohesion: 0.12
Nodes (6): InvoiceAgent, InvoiceRequest, InvoiceAgentResponse, test_invoice_agent_does_not_treat_invoice_id_as_customer_id(), test_invoice_agent_missing_customer_id_fails_validation(), test_invoice_agent_parse_request()

### Community 7 - "Music Agent Tools"
Cohesion: 0.13
Nodes (9): MCPToolAgent, MusicAgent, MusicRequest, MusicAgentResponse, test_music_agent_missing_artist_fails_validation(), test_music_agent_parses_artist_requests(), test_music_agent_parses_genre_requests(), test_music_agent_parses_song_check_requests() (+1 more)

### Community 8 - "Planner Execution Nodes"
Cohesion: 0.15
Nodes (21): _attach_a2a_payload(), _copy_planner_output(), _failure_result(), _get_next_task_for_agent(), invoice_node(), _mark_task_failed(), missing_info_node(), music_node() (+13 more)

### Community 9 - "Planner Schema Validation"
Cohesion: 0.11
Nodes (14): get_llm(), _has_arg_value(), _instruction_must_not_be_blank(), _validate_agent_intent_and_required_fields(), _validate_output_consistency(), PlannerAgent, FailingPlannerAgent, RepairablePlannerAgent (+6 more)

### Community 10 - "Task Instruction Builder"
Cohesion: 0.16
Nodes (23): build_a2a_payload_from_task(), build_instruction_from_task(), Raised when a planner task cannot be converted into an executable instruction., _require_arg(), _require_task_field(), TaskInstructionError, test_build_a2a_payload_copies_args(), test_build_a2a_payload_from_all_invoices_task() (+15 more)

### Community 11 - "Response Aggregation"
Cohesion: 0.17
Nodes (15): AggregatorAgent, AgentResult, AggregatorInput, AggregatorOutput, final_response_node(), aggregate(), test_aggregator_combines_multiple_agent_results_in_order(), test_aggregator_formats_dict_result_without_data() (+7 more)

### Community 12 - "Invoice A2A Executor"
Cohesion: 0.11
Nodes (10): AgentExecutor, load_agent_card(), Invoice Agent Card, InvoiceAgentExecutor, create_app(), main(), Music Agent Card, MusicAgentExecutor (+2 more)

### Community 13 - "Args-First Contract Tests"
Cohesion: 0.12
Nodes (21): Task Args Are the Source of Executable Instructions, build_a2a_payload_from_task, build_instruction_from_task, TaskInstructionError, Typed A2A Client Instruction Construction Tests, Planner A2A Payload Integration Tests, Aggregator Result Formatting and Ordering Tests, Planner Checkpointer Backend Tests (+13 more)

### Community 14 - "End-to-End Flow Fixtures"
Cohesion: 0.25
Nodes (15): FakePlanner, FakePlannerOutput, _invoke_graph(), _set_planner_output(), _task(), test_planner_e2e_all_invoices_query_uses_args_first_instruction(), test_planner_e2e_ambiguous_music_can_choose_artist_after_hitl(), test_planner_e2e_ambiguous_music_defaults_to_genre_after_hitl() (+7 more)

### Community 15 - "Human Review Logic"
Cohesion: 0.18
Nodes (18): ask_for_missing_info(), _extract_labeled_value(), extract_missing_fields(), interrupt_for_missing_info(), test_ask_for_missing_artist(), test_ask_for_missing_genre(), test_ask_for_missing_music_search_type(), test_ask_for_missing_song_title() (+10 more)

### Community 16 - "Response Integration"
Cohesion: 0.16
Nodes (18): Structured Agent Result Formatting, AgentResult, MCPToolAgent.call_tool, InvoiceAgentResponse, MusicAgent, MusicRequest, MusicAgent.ainvoke, check_for_songs Capability (+10 more)

### Community 17 - "Orchestrator Service Flow"
Cohesion: 0.13
Nodes (18): Planner Invoke HTTP Endpoint, PlannerInvokeRequest, PlannerService.invoke, PlannerServiceResponse, Planner LangGraph Workflow, Final Response Graph Node, Missing Information Interrupt Flow, Invoice Execution Graph Node (+10 more)

### Community 18 - "Checkpoint Management"
Cohesion: 0.14
Nodes (13): build_async_checkpointer_context(), build_memory_checkpointer(), Checkpointer factory for the planner LangGraph app., Build an in-memory checkpointer for tests and simple local runs., Build the configured checkpointer.      Supported backends:     - memory: volati, build_graph(), main(), test_async_checkpointer_context_is_case_insensitive() (+5 more)

### Community 19 - "HITL Repair Tests"
Cohesion: 0.13
Nodes (18): extract_missing_fields HITL Parsing, ask_for_missing_info HITL Prompts, music_search_type Clarification, Invalid Agent Intent Repair, Missing Required Argument Repair, Generic Music Request Clarification Repair, Repair Prompt Contract, Safe Failed Planner Output (+10 more)

### Community 20 - "Invoice Agent Card"
Cohesion: 0.18
Nodes (10): capabilities, pushNotifications, streaming, defaultInputModes, defaultOutputModes, description, name, skills (+2 more)

### Community 21 - "Music Agent Card"
Cohesion: 0.18
Nodes (10): capabilities, pushNotifications, streaming, defaultInputModes, defaultOutputModes, description, name, skills (+2 more)

### Community 23 - "A2A Error Tests"
Cohesion: 0.39
Nodes (7): make_client(), test_send_message_raises_on_connection_error(), test_send_message_raises_on_http_500(), test_send_message_raises_on_invalid_json(), test_send_message_raises_on_jsonrpc_error(), test_send_message_raises_on_timeout(), test_send_message_returns_jsonrpc_body()

### Community 25 - "Graphify Instructions"
Cohesion: 0.40
Nodes (5): Graphify Workflow, Repository Instructions, Runtime Configuration, Service Start Order, Graphify PreToolUse Hook Check

### Community 26 - "Architecture Documentation"
Cohesion: 0.40
Nodes (5): A2A Agent-to-Agent Communication, Chinook SQLite Database, FastMCP Database Tools, LangGraph Orchestration, Multi-Agent System With LangGraph A2A And MCP

### Community 27 - "Transport Integration Tests"
Cohesion: 0.40
Nodes (5): A2A JSON-RPC Transport Error Handling Tests, A2A Response Text Extraction Tests, Invoice A2A JSON-RPC Integration Test, MCP Tool Agent Result Normalization and Error Tests, Music A2A JSON-RPC Integration Test

### Community 28 - "MCP Tool Surface"
Cohesion: 0.67
Nodes (4): MCP Database Provider, Invoice MCP Tool Family, Music MCP Tool Family, MCP Server Assembly

## Knowledge Gaps
- **61 isolated node(s):** `PreToolUse`, `name`, `description`, `supportedInterfaces`, `version` (+56 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MCPToolAgent` connect `Shared Tool Errors` to `Invoice Agent Logic`, `Music Agent Tools`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `build_async_checkpointer_context()` connect `Checkpoint Management` to `Planner Schema Validation`, `Shared Tool Errors`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `final_response_node()` connect `Response Aggregation` to `Planner Execution Nodes`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `MusicAgent` (e.g. with `MCPToolAgent` and `test_music_agent_parses_artist_requests()`) actually correct?**
  _`MusicAgent` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `InvoiceAgent` (e.g. with `MCPToolAgent` and `test_invoice_agent_parse_request()`) actually correct?**
  _`InvoiceAgent` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `MCPToolAgent` (e.g. with `FakeTool` and `FakeClient`) actually correct?**
  _`MCPToolAgent` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `PlannerService` (e.g. with `FakeGraph` and `FakeInterrupt`) actually correct?**
  _`PlannerService` has 12 INFERRED edges - model-reasoned connections that need verification._