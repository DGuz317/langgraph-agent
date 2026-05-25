# Graph Report - langgraph-agent  (2026-05-25)

## Corpus Check
- 94 files · ~22,641 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 853 nodes · 1247 edges · 86 communities (74 shown, 12 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 291 edges (avg confidence: 0.79)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `04e4ae45`
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
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]

## God Nodes (most connected - your core abstractions)
1. `MusicAgent` - 27 edges
2. `PlannerService` - 22 edges
3. `InvoiceAgent` - 22 edges
4. `PlannerServiceResponse` - 19 edges
5. `MCPToolAgent` - 18 edges
6. `_call_tool()` - 17 edges
7. `invoice_node()` - 15 edges
8. `Multi-Agent System with LangGraph, A2A, and MCP` - 15 edges
9. `build_instruction_from_task()` - 14 edges
10. `PlannedTask` - 14 edges

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

## Communities (86 total, 12 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.10
Nodes (23): create_app(), PlannerServiceProtocol, _extract_final_answer(), _extract_interrupt_message(), _has_interrupt(), PlannerService, Return result as-is when possible.      Kept as a helper so future API layers ca, Reusable runtime wrapper for planner graph invocation. (+15 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (36): Domain Boundary Rule, A2A Endpoint Settings, Model Provider Configuration, Settings, SQLITE_DB Configuration, InvoiceA2AClient, InvoiceAgent, InvoiceAgent.ainvoke() (+28 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (14): BaseA2AClient, Send structured task data while retaining text compatibility., MusicA2AClient, BaseA2AClient, A2AClientError, Raised when an A2A service request fails., StubA2AClient, test_ask_combines_multiple_text_parts() (+6 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (32): get_db(), create_mcp_server(), main(), _assert_non_empty_list_of_dicts(), _call_tool(), _call_tool_async(), db(), _extract_tool_data() (+24 more)

### Community 4 - "Community 4"
Cohesion: 0.12
Nodes (18): MCPToolError, MultiAgentSystemError, Raised when an MCP tool call fails., Base error for application-level failures., MCPToolAgent, Base class for agents that call tools exposed by the MCP server., RuntimeError, FakeClient (+10 more)

### Community 5 - "Community 5"
Cohesion: 0.10
Nodes (21): get_llm(), PlannerAgent, PlannedTask, PlannerOutput, test_normalize_output_adds_task_id_and_sets_status(), test_normalize_output_preserves_task_args(), test_planned_task_accepts_all_invoices_task(), test_planned_task_accepts_clarify_music_search_with_missing_search_type() (+13 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (9): InvoiceAgent, InvoiceRequest, InvoiceAgentResponse, InvoiceRequest, InvoiceTaskPayload, MCPToolAgent, test_invoice_agent_does_not_treat_invoice_id_as_customer_id(), test_invoice_agent_missing_customer_id_fails_validation() (+1 more)

### Community 7 - "Community 7"
Cohesion: 0.14
Nodes (8): MusicAgent, MusicRequest, MusicAgentResponse, test_music_agent_missing_artist_fails_validation(), test_music_agent_parses_artist_requests(), test_music_agent_parses_genre_requests(), test_music_agent_parses_song_check_requests(), test_song_title_with_genre_word_does_not_become_genre_request()

### Community 8 - "Community 8"
Cohesion: 0.14
Nodes (22): _attach_a2a_payload(), _copy_planner_output(), _failure_result(), final_response_node(), _get_next_task_for_agent(), invoice_node(), _mark_task_failed(), missing_info_node() (+14 more)

### Community 9 - "Community 9"
Cohesion: 0.11
Nodes (16): PlannerInvokeRequest, API request for invoking or resuming the planner., _user_input_must_not_be_blank(), _has_arg_value(), _instruction_must_not_be_blank(), _validate_agent_intent_and_required_fields(), _validate_output_consistency(), PlannerAgent (+8 more)

### Community 10 - "Community 10"
Cohesion: 0.16
Nodes (23): build_a2a_payload_from_task(), build_instruction_from_task(), Raised when a planner task cannot be converted into an executable instruction., _require_arg(), _require_task_field(), TaskInstructionError, test_build_a2a_payload_copies_args(), test_build_a2a_payload_from_all_invoices_task() (+15 more)

### Community 11 - "Community 11"
Cohesion: 0.14
Nodes (17): AggregatorAgent, AgentResult, AggregatorInput, AggregatorOutput, BaseModel, MusicRequest, MusicTaskPayload, aggregate() (+9 more)

### Community 12 - "Community 12"
Cohesion: 0.09
Nodes (16): AgentExecutor, load_agent_card(), Invoice Agent Card, InvoiceAgentExecutor, create_app(), main(), Music Agent Card, MusicAgentExecutor (+8 more)

### Community 13 - "Community 13"
Cohesion: 0.12
Nodes (21): Task Args Are the Source of Executable Instructions, build_a2a_payload_from_task, build_instruction_from_task, TaskInstructionError, Typed A2A Client Instruction Construction Tests, Planner A2A Payload Integration Tests, Aggregator Result Formatting and Ordering Tests, Planner Checkpointer Backend Tests (+13 more)

### Community 14 - "Community 14"
Cohesion: 0.25
Nodes (15): FakePlanner, FakePlannerOutput, _invoke_graph(), _set_planner_output(), _task(), test_planner_e2e_all_invoices_query_uses_args_first_instruction(), test_planner_e2e_ambiguous_music_can_choose_artist_after_hitl(), test_planner_e2e_ambiguous_music_defaults_to_genre_after_hitl() (+7 more)

### Community 15 - "Community 15"
Cohesion: 0.18
Nodes (18): ask_for_missing_info(), _extract_labeled_value(), extract_missing_fields(), interrupt_for_missing_info(), test_ask_for_missing_artist(), test_ask_for_missing_genre(), test_ask_for_missing_music_search_type(), test_ask_for_missing_song_title() (+10 more)

### Community 16 - "Community 16"
Cohesion: 0.16
Nodes (18): Structured Agent Result Formatting, AgentResult, MCPToolAgent.call_tool, InvoiceAgentResponse, MusicAgent, MusicRequest, MusicAgent.ainvoke, check_for_songs Capability (+10 more)

### Community 17 - "Community 17"
Cohesion: 0.13
Nodes (18): Planner Invoke HTTP Endpoint, PlannerInvokeRequest, PlannerService.invoke, PlannerServiceResponse, Planner LangGraph Workflow, Final Response Graph Node, Missing Information Interrupt Flow, Invoice Execution Graph Node (+10 more)

### Community 18 - "Community 18"
Cohesion: 0.14
Nodes (13): build_async_checkpointer_context(), build_memory_checkpointer(), Checkpointer factory for the planner LangGraph app., Build an in-memory checkpointer for tests and simple local runs., Build the configured checkpointer.      Supported backends:     - memory: volati, build_graph(), main(), test_async_checkpointer_context_is_case_insensitive() (+5 more)

### Community 19 - "Community 19"
Cohesion: 0.13
Nodes (18): extract_missing_fields HITL Parsing, ask_for_missing_info HITL Prompts, music_search_type Clarification, Invalid Agent Intent Repair, Missing Required Argument Repair, Generic Music Request Clarification Repair, Repair Prompt Contract, Safe Failed Planner Output (+10 more)

### Community 20 - "Community 20"
Cohesion: 0.18
Nodes (10): capabilities, pushNotifications, streaming, defaultInputModes, defaultOutputModes, description, name, skills (+2 more)

### Community 21 - "Community 21"
Cohesion: 0.18
Nodes (10): capabilities, pushNotifications, streaming, defaultInputModes, defaultOutputModes, description, name, skills (+2 more)

### Community 23 - "Community 23"
Cohesion: 0.36
Nodes (8): make_client(), test_ask_payload_sends_data_and_compatibility_text_parts(), test_send_message_raises_on_connection_error(), test_send_message_raises_on_http_500(), test_send_message_raises_on_invalid_json(), test_send_message_raises_on_jsonrpc_error(), test_send_message_raises_on_timeout(), test_send_message_returns_jsonrpc_body()

### Community 25 - "Community 25"
Cohesion: 0.40
Nodes (5): Graphify Workflow, Repository Instructions, Runtime Configuration, Service Start Order, Graphify PreToolUse Hook Check

### Community 26 - "Community 26"
Cohesion: 0.40
Nodes (5): A2A Agent-to-Agent Communication, Chinook SQLite Database, FastMCP Database Tools, LangGraph Orchestration, Multi-Agent System With LangGraph A2A And MCP

### Community 27 - "Community 27"
Cohesion: 0.40
Nodes (5): A2A JSON-RPC Transport Error Handling Tests, A2A Response Text Extraction Tests, Invoice A2A JSON-RPC Integration Test, MCP Tool Agent Result Normalization and Error Tests, Music A2A JSON-RPC Integration Test

### Community 28 - "Community 28"
Cohesion: 0.67
Nodes (4): MCP Database Provider, Invoice MCP Tool Family, Music MCP Tool Family, MCP Server Assembly

### Community 73 - "Community 73"
Cohesion: 0.08
Nodes (28): acontext_session_id(), AcontextCapture, build_acontext_capture(), _ensure_session(), PlannerInteractionCapture, Map existing planner thread identifiers into stable Acontext UUIDs., Store one planner interaction., Capture user-visible planner turns in Acontext. (+20 more)

### Community 74 - "Community 74"
Cohesion: 0.06
Nodes (30): code:text (User input), code:bash (uv run pytest tests/test_invoice_agent_parsing.py tests/test), code:bash (RUN_INVOICE_SUPPORT_INTEGRATION_TESTS=1 uv run pytest tests/), code:text (Get all invoices for customer_id=5), code:json ({), code:text (invoice -> music -> final_response), code:text (invoice -\), code:text (latest_invoice -> {latest_invoice, support_employee}) (+22 more)

### Community 75 - "Community 75"
Cohesion: 0.22
Nodes (9): 1. Start MCP server, 2. Start Invoice A2A service, 3. Start Music A2A service, 4. Run Planner CLI, code:bash (uv run python scripts/run_mcp_server.py --host localhost --p), code:bash (uv run python scripts/run_invoice_a2a.py --host localhost --), code:bash (uv run python scripts/run_music_a2a.py --host localhost --po), code:bash (uv run python scripts/run_planner.py) (+1 more)

### Community 76 - "Community 76"
Cohesion: 0.15
Nodes (12): Architecture, code:text (User query), code:text (multi-agent-system/), code:text (Planner → optional HITL → invoice/music task execution → agg), Core Components, Current Capabilities, Current Status, Design Principles (+4 more)

### Community 77 - "Community 77"
Cohesion: 0.22
Nodes (8): Architecture Notes, Commands, Graphify, graphify, Repository Instructions, Runtime Flow, Stack And Setup, Workflow

### Community 78 - "Community 78"
Cohesion: 0.22
Nodes (9): code:bash (uv run pytest tests -q), code:bash (uv run pytest tests/test_aggregator.py -q), code:bash (RUN_LLM_TESTS=1 uv run pytest tests/test_llm_planner.py -q), code:bash (RUN_MCP_INTEGRATION_TESTS=1 uv run pytest tests/test_mcp_too), code:bash (RUN_A2A_INTEGRATION_TESTS=1 uv run pytest tests/test_invoice), code:bash (RUN_ORCHESTRATOR_API_INTEGRATION_TESTS=1 uv run pytest tests), code:bash (RUN_A2A_PAYLOAD_INTEGRATION_TESTS=1 uv run pytest tests/test), code:bash (RUN_INVOICE_SUPPORT_INTEGRATION_TESTS=1 uv run pytest tests/) (+1 more)

### Community 79 - "Community 79"
Cohesion: 0.29
Nodes (7): code:text (Get latest invoice for customer_id=5), code:text (Find tracks by artist AC/DC), code:text (User: What is my latest invoice?), code:text (User: Recommend some songs), code:text (User: Recommend some songs), code:text (Get latest invoice for customer_id=5 and find tracks by arti), Example Prompts

### Community 80 - "Community 80"
Cohesion: 0.40
Nodes (5): A2A integration test fails with connection error, code:bash (uv run pytest tests -q), code:text (1. Add or update schema.), code:bash (uv run python scripts/run_mcp_server.py --host localhost --p), Development Workflow

### Community 81 - "Community 81"
Cohesion: 0.67
Nodes (3): code:text (graphify-out/), code:bash (graphify update .), Knowledge Graph

### Community 82 - "Community 82"
Cohesion: 0.67
Nodes (3): code:bash (uv sync), code:env (MODEL_PROVIDER=ollama), Setup

### Community 84 - "Community 84"
Cohesion: 0.24
Nodes (7): InvoiceA2AClient, _assert_support_employee(), _response_data(), test_invoice_a2a_all_invoices_include_support_employee(), test_invoice_a2a_latest_invoice_includes_support_employee(), test_invoice_a2a_returns_support_employee_for_latest_invoice(), test_invoice_a2a_unit_price_invoices_include_support_employee()

### Community 85 - "Community 85"
Cohesion: 0.50
Nodes (4): 5. Or run Planner API, code:http (POST http://localhost:12000/planner/invoke), code:json ({), code:bash (uv run python scripts/run_orchestrator_api.py --host localho)

## Knowledge Gaps
- **126 isolated node(s):** `PreToolUse`, `name`, `description`, `supportedInterfaces`, `version` (+121 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PlannerServiceResponse` connect `Community 73` to `Community 0`, `Community 9`, `Community 11`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `MCPToolAgent` connect `Community 4` to `Community 6`, `Community 7`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `PlannerService` connect `Community 0` to `Community 73`, `Community 18`, `Community 4`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `MusicAgent` (e.g. with `MCPToolAgent` and `test_music_agent_parses_artist_requests()`) actually correct?**
  _`MusicAgent` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `PlannerService` (e.g. with `FakeGraph` and `FakeInterrupt`) actually correct?**
  _`PlannerService` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `InvoiceAgent` (e.g. with `MCPToolAgent` and `test_invoice_agent_parse_request()`) actually correct?**
  _`InvoiceAgent` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `PlannerServiceResponse` (e.g. with `FakePlannerService` and `PlannerService`) actually correct?**
  _`PlannerServiceResponse` has 16 INFERRED edges - model-reasoned connections that need verification._