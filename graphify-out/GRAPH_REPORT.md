# Graph Report - langgraph-agent  (2026-05-29)

## Corpus Check
- 101 files · ~33,433 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2305 nodes · 3636 edges · 113 communities (100 shown, 13 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 418 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1005c1e8`
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
- [[_COMMUNITY_Community 33|Community 33]]
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
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 91|Community 91]]
- [[_COMMUNITY_Community 92|Community 92]]
- [[_COMMUNITY_Community 93|Community 93]]
- [[_COMMUNITY_Community 94|Community 94]]
- [[_COMMUNITY_Community 95|Community 95]]
- [[_COMMUNITY_Community 96|Community 96]]
- [[_COMMUNITY_Community 97|Community 97]]
- [[_COMMUNITY_Community 98|Community 98]]
- [[_COMMUNITY_Community 99|Community 99]]
- [[_COMMUNITY_Community 100|Community 100]]
- [[_COMMUNITY_Community 101|Community 101]]
- [[_COMMUNITY_Community 102|Community 102]]
- [[_COMMUNITY_Community 103|Community 103]]
- [[_COMMUNITY_Community 104|Community 104]]
- [[_COMMUNITY_Community 105|Community 105]]
- [[_COMMUNITY_Community 106|Community 106]]
- [[_COMMUNITY_Community 107|Community 107]]
- [[_COMMUNITY_Community 108|Community 108]]
- [[_COMMUNITY_Community 109|Community 109]]
- [[_COMMUNITY_Community 110|Community 110]]
- [[_COMMUNITY_Community 111|Community 111]]
- [[_COMMUNITY_Community 112|Community 112]]

## God Nodes (most connected - your core abstractions)
1. `post()` - 37 edges
2. `get()` - 37 edges
3. `PlannerService` - 32 edges
4. `InvoiceAgent` - 31 edges
5. `fetch()` - 29 edges
6. `PlannerServiceResponse` - 28 edges
7. `ExecutionEvidence` - 28 edges
8. `MusicAgent` - 28 edges
9. `debug()` - 27 edges
10. `getSandbox()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `Graphify PreToolUse Hook Check` --implements--> `Graphify Workflow`  [INFERRED]
  .codex/hooks.json → AGENTS.md
- `Design Principles` --semantically_similar_to--> `Domain Boundary Rule`  [INFERRED] [semantically similar]
  README.md → AGENTS.md
- `InvoiceAgent` --implements--> `Invoice Support Employee Enrichment Rule`  [INFERRED]
  src/multi_agent_system/a2a_servers/invoice_agent/agent.py → PROJECT.md
- `test_acontext_memory_recall_failed_when_client_errors()` --calls--> `AcontextMemoryRecall`  [INFERRED]
  tests/test_acontext_memory.py → src/multi_agent_system/orchestrator/acontext_memory.py
- `test_build_latest_invoice_instruction()` --calls--> `build_instruction_from_task()`  [INFERRED]
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

## Communities (113 total, 13 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.15
Nodes (22): MemoryRecallResult, PlannerService, Reusable runtime wrapper for planner graph invocation., Reusable runtime wrapper for planner graph invocation., Reusable runtime wrapper for planner graph invocation., Reusable runtime wrapper for planner graph invocation., RuntimeError, FakeCapture (+14 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (36): Domain Boundary Rule, A2A Endpoint Settings, Model Provider Configuration, Settings, SQLITE_DB Configuration, InvoiceA2AClient, InvoiceAgent, InvoiceAgent.ainvoke() (+28 more)

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (25): MCPToolError, MultiAgentSystemError, Raised when an MCP tool call fails., Base error for application-level failures., collect_execution_evidence(), Collect evidence for one request without leaking across concurrent tasks., Append evidence when a collection scope is active., record_execution_evidence() (+17 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (40): get_db(), create_mcp_server(), main(), # TODO: In the future, we will not separate into 2 tool sets, we will create que, _assert_non_empty_list_of_dicts(), _call_tool(), _call_tool_async(), db() (+32 more)

### Community 4 - "Community 4"
Cohesion: 0.02
Nodes (38): assert(), binding(), cleanup(), cpuUsage(), createNotImplementedError(), currentEvent, decoder, desc (+30 more)

### Community 5 - "Community 5"
Cohesion: 0.20
Nodes (18): PlannedTask, test_planned_task_accepts_all_invoices_task(), test_planned_task_accepts_clarify_music_search_with_missing_search_type(), test_planned_task_accepts_complete_invoice_task(), test_planned_task_accepts_customer_support_employee_task(), test_planned_task_accepts_invoice_detail_task(), test_planned_task_accepts_invoice_query_and_enforces_support_employee(), test_planned_task_accepts_invoice_summary_task() (+10 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (14): InvoiceAgent, InvoiceRequest, _positive_int(), # TODO: Reduce if else rule-based  more about dynamic and practical. IT should b, InvoiceAgentResponse, InvoiceRequest, InvoiceTaskPayload, # TODO: This (+6 more)

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (35): ExecutionEvidence, Sanitized workflow evidence eligible for long-lived memory storage., _agent_result_evidence(), _attach_a2a_payload(), _copy_planner_output(), _dispatch_evidence(), _extract_remote_evidence(), _failure_result() (+27 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (30): AggregatorAgent, AgentResult, AggregatorInput, AggregatorOutput, BaseModel, MCPToolAgent, MusicAgent, MusicRequest (+22 more)

### Community 9 - "Community 9"
Cohesion: 0.00
Nodes (661): AbortController, Ai_Cf_Ai4Bharat_Indictrans2_En_Indic_1B_Input, Ai_Cf_Ai4Bharat_Indictrans2_En_Indic_1B_Output, Ai_Cf_Aisingapore_Gemma_Sea_Lion_V4_27B_It_Async_Batch, Ai_Cf_Aisingapore_Gemma_Sea_Lion_V4_27B_It_AsyncResponse, Ai_Cf_Aisingapore_Gemma_Sea_Lion_V4_27B_It_Chat_Completion_Response, Ai_Cf_Aisingapore_Gemma_Sea_Lion_V4_27B_It_Input, Ai_Cf_Aisingapore_Gemma_Sea_Lion_V4_27B_It_JSON_Mode (+653 more)

### Community 10 - "Community 10"
Cohesion: 0.12
Nodes (32): build_a2a_payload_from_task(), build_instruction_from_task(), _build_invoice_query_instruction(), _build_music_query_instruction(), _has_arg(), _optional_arg(), Raised when a planner task cannot be converted into an executable instruction., _require_arg() (+24 more)

### Community 11 - "Community 11"
Cohesion: 0.11
Nodes (17): dependencies, @cloudflare/sandbox, description, devDependencies, @cloudflare/workers-types, typescript, wrangler, engines (+9 more)

### Community 12 - "Community 12"
Cohesion: 0.10
Nodes (20): AgentExecutor, load_agent_card(), Invoice Agent Card, InvoiceAgentExecutor, create_app(), main(), Music Agent Card, MusicAgentExecutor (+12 more)

### Community 13 - "Community 13"
Cohesion: 0.12
Nodes (21): Task Args Are the Source of Executable Instructions, build_a2a_payload_from_task, build_instruction_from_task, TaskInstructionError, Typed A2A Client Instruction Construction Tests, Planner A2A Payload Integration Tests, Aggregator Result Formatting and Ordering Tests, Planner Checkpointer Backend Tests (+13 more)

### Community 14 - "Community 14"
Cohesion: 0.22
Nodes (18): FakePlanner, FakePlannerOutput, _invoke_graph(), _set_planner_output(), _task(), test_planner_e2e_all_invoices_query_uses_args_first_instruction(), test_planner_e2e_ambiguous_music_can_choose_artist_after_hitl(), test_planner_e2e_ambiguous_music_defaults_to_genre_after_hitl() (+10 more)

### Community 15 - "Community 15"
Cohesion: 0.16
Nodes (21): ask_for_missing_info(), _extract_labeled_value(), extract_missing_fields(), interrupt_for_missing_info(), test_ask_for_missing_artist(), test_ask_for_missing_genre(), test_ask_for_missing_invoice_id(), test_ask_for_missing_music_search_type() (+13 more)

### Community 16 - "Community 16"
Cohesion: 0.16
Nodes (18): Structured Agent Result Formatting, AgentResult, MCPToolAgent.call_tool, InvoiceAgentResponse, MusicAgent, MusicRequest, MusicAgent.ainvoke, check_for_songs Capability (+10 more)

### Community 17 - "Community 17"
Cohesion: 0.13
Nodes (18): Planner Invoke HTTP Endpoint, PlannerInvokeRequest, PlannerService.invoke, PlannerServiceResponse, Planner LangGraph Workflow, Final Response Graph Node, Missing Information Interrupt Flow, Invoice Execution Graph Node (+10 more)

### Community 18 - "Community 18"
Cohesion: 0.13
Nodes (14): path(), build_async_checkpointer_context(), build_memory_checkpointer(), Checkpointer factory for the planner LangGraph app., Build an in-memory checkpointer for tests and simple local runs., Build the configured checkpointer.      Supported backends:     - memory: volati, build_graph(), main() (+6 more)

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

### Community 32 - "Community 32"
Cohesion: 0.40
Nodes (4): BaseSettings, # TODO: Langsmith can not track eventhough i had enabled langsmith tracing, # TODO: Too many tests. Only keep or combine all the test into specific tests pe, Settings

### Community 33 - "Community 33"
Cohesion: 0.15
Nodes (4): _create_fast_planner_app(), FakePlanner, FakePlannerOutput, test_real_planner_api_records_structured_a2a_payloads()

### Community 73 - "Community 73"
Cohesion: 0.05
Nodes (51): acontext_session_id(), AcontextCapture, build_acontext_capture(), _ensure_learning_session(), _ensure_session(), _extract_execution_evidence(), _field_names(), _interaction_evidence() (+43 more)

### Community 74 - "Community 74"
Cohesion: 0.07
Nodes (31): code:text (User input), code:bash (uv run pytest tests -q), code:bash (uv run pytest tests/test_invoice_agent_parsing.py tests/test), code:bash (RUN_INVOICE_SUPPORT_INTEGRATION_TESTS=1 uv run pytest tests/), code:text (Get all invoices for customer_id=5), code:json ({), code:text (invoice -> music -> final_response), code:text (invoice -\) (+23 more)

### Community 75 - "Community 75"
Cohesion: 0.08
Nodes (42): buildLogData(), buildMessage(), checkVersionCompatibility(), connectViaFetch(), containerPathToR2Key(), debug(), deleteFile(), emitWarning() (+34 more)

### Community 76 - "Community 76"
Cohesion: 0.06
Nodes (58): 1. Start MCP server, 2. Start Invoice A2A service, 3. Start Music A2A service, 4. Run Planner CLI, 5. Or run Planner API, A2A integration test fails with connection error, Architecture, code:text (User query) (+50 more)

### Community 77 - "Community 77"
Cohesion: 0.22
Nodes (8): Architecture Notes, Commands, Graphify, graphify, Repository Instructions, Runtime Flow, Stack And Setup, Workflow

### Community 78 - "Community 78"
Cohesion: 0.06
Nodes (43): base64ToUint8Array(), checkout(), click(), createProcessFromDTO(), createSession(), doubleClick(), drag(), ensureDefaultSession() (+35 more)

### Community 79 - "Community 79"
Cohesion: 0.08
Nodes (40): checkAuth(), constructPreviewUrl(), createErrorFromResponse(), determinePort(), exec(), exposePort(), fetch(), fromHeaders() (+32 more)

### Community 80 - "Community 80"
Cohesion: 0.06
Nodes (44): abort(), addEventListener(), addTimeoutSignal(), alarm(), callOnStop(), containerFetch(), deleteSchedules(), generateId() (+36 more)

### Community 81 - "Community 81"
Cohesion: 0.16
Nodes (20): buildSandboxConfiguration(), getSandbox(), hasSandboxConfiguration(), mergeSandboxConfiguration(), sameContainerTimeouts(), checkAuth(), CreateSandboxRequest, DownloadFileRequest (+12 more)

### Community 82 - "Community 82"
Cohesion: 0.15
Nodes (13): API Endpoints, code:bash (POST /sandbox/create), code:json ({), code:bash (POST /sandbox/{sandbox_id}/kill), code:json ({), code:bash (GET /sandbox/{sandbox_id}), code:json ({), code:bash (POST /sandbox/{sandbox_id}/update) (+5 more)

### Community 84 - "Community 84"
Cohesion: 0.06
Nodes (29): BaseA2AClient, Send structured task data while retaining text compatibility., InvoiceA2AClient, MusicA2AClient, BaseA2AClient, A2AClientError, Raised when an A2A service request fails., StubA2AClient (+21 more)

### Community 85 - "Community 85"
Cohesion: 0.17
Nodes (11): Architecture, Authentication, Cloudflare Sandbox Worker API, code:block1 (Python Core → CloudflareSandboxBackend → HTTP API → Cloudfla), code:bash (npx wrangler secret put AUTH_TOKEN), code:bash (Authorization: Bearer <your-token>), Configuration, Dockerfile (+3 more)

### Community 86 - "Community 86"
Cohesion: 0.22
Nodes (9): After Deployment, code:bash (npx wrangler deploy), code:bash (npx wrangler secret put AUTH_TOKEN), code:bash (npx wrangler containers list), code:block24 (https://cloudflare.your-subdomain.workers.dev), Deploy to Cloudflare Workers, Production Deployment, Set Secrets (if using authentication) (+1 more)

### Community 87 - "Community 87"
Cohesion: 0.29
Nodes (7): code:bash (pnpm install), code:bash (pnpm run dev), code:bash (# Test create sandbox), Local Development, Prerequisites, Setup, Testing

### Community 88 - "Community 88"
Cohesion: 0.40
Nodes (5): Authentication Errors, code:bash (npx wrangler tail), Connection Refused (Local Dev), Container Not Ready, Troubleshooting

### Community 89 - "Community 89"
Cohesion: 0.13
Nodes (24): buildS3fsSource(), createPasswordFile(), delete(), deletePasswordFile(), destroy(), detectCredentials(), detectProviderFromUrl(), execInternal() (+16 more)

### Community 90 - "Community 90"
Cohesion: 0.50
Nodes (4): code:yaml (sandbox_type: "cloudflare"), Configuration, Integration with Python Core, Usage

### Community 91 - "Community 91"
Cohesion: 0.67
Nodes (3): code:bash (POST /sandbox/{sandbox_id}/download), code:json ({), Download File

### Community 92 - "Community 92"
Cohesion: 0.67
Nodes (3): code:bash (POST /sandbox/{sandbox_id}/upload), code:json ({), Upload File

### Community 93 - "Community 93"
Cohesion: 0.21
Nodes (8): PlannerAgent, FailingPlannerAgent, RepairablePlannerAgent, test_planner_repairs_generic_music_request_to_clarify_search(), test_planner_repairs_invalid_agent_intent_pair(), test_planner_repairs_missing_required_arg_with_hitl_missing_field(), test_planner_returns_safe_failed_output_when_repair_fails(), test_repair_prompt_contains_original_input_and_error()

### Community 94 - "Community 94"
Cohesion: 0.11
Nodes (27): createArchive(), createBackup(), deleteSession(), doCreateBackup(), doRestoreBackup(), downloadBackupPresigned(), enqueueBackupOp(), ensureBackupSession() (+19 more)

### Community 95 - "Community 95"
Cohesion: 0.09
Nodes (26): buildStreamOptions(), buildUrl(), connect(), connectViaWebSocket(), doConnect(), doFetch(), doStreamFetch(), fetchStream() (+18 more)

### Community 96 - "Community 96"
Cohesion: 0.27
Nodes (11): applySandboxConfiguration(), computeRetryTimeoutMs(), configure(), createSandboxClient(), setBaseUrl(), setContainerTimeouts(), setKeepAlive(), setRetryTimeoutMs() (+3 more)

### Community 97 - "Community 97"
Cohesion: 0.20
Nodes (12): createCodeContext(), deleteCodeContext(), executeWithRetry(), getOrCreateDefaultContext(), isRetryableError(), listCodeContexts(), operation(), runCode() (+4 more)

### Community 98 - "Community 98"
Cohesion: 0.25
Nodes (6): __Facade_ScheduledController__, wrapExportedHandler(), wrapWorkerEntrypoint(), __facade_register__(), wrapExportedHandler(), wrapWorkerEntrypoint()

### Community 99 - "Community 99"
Cohesion: 0.14
Nodes (12): AcontextMemoryRecall, Retrieve sanitized Acontext skills for planner guidance., Retrieve sanitized Acontext skills for planner guidance., FakeClient, FakeLearningSpaces, FakeSkills, _skill(), test_acontext_memory_recall_empty_when_no_learning_space() (+4 more)

### Community 100 - "Community 100"
Cohesion: 0.19
Nodes (7): get_llm(), _has_arg_value(), _instruction_must_not_be_blank(), # TODO: This is the rule-based tasks intent, can we switch out for more practica, _validate_agent_intent_and_required_fields(), _validate_output_consistency(), ValueError

### Community 101 - "Community 101"
Cohesion: 0.18
Nodes (14): bind(), child(), constructor(), createLogger(), createNoOpLogger(), createTransport(), encodeRfc3986(), generate() (+6 more)

### Community 103 - "Community 103"
Cohesion: 0.14
Nodes (16): build_acontext_memory_recall(), _call_skill_selector(), _compact(), disabled_memory_result(), failed_memory_result(), _FailedMemoryRecall, _format_memory_context(), _get_skill_markdown() (+8 more)

### Community 104 - "Community 104"
Cohesion: 0.15
Nodes (14): command(), _extract_final_answer(), _extract_interrupt_message(), _has_interrupt(), Return result as-is when possible.      Kept as a helper so future API layers ca, Return result as-is when possible.      Kept as a helper so future API layers ca, Return result as-is when possible.      Kept as a helper so future API layers ca, Return graph result without internal prompt-injection context.      Kept as a he (+6 more)

### Community 105 - "Community 105"
Cohesion: 0.12
Nodes (11): PlannerInteractionCapture, Store one planner interaction., Store one user-visible planner interaction., Store one user-visible planner interaction., PlannerMemoryRecall, Return sanitized memory guidance for one planner request., Return sanitized memory guidance for one planner request., create_app() (+3 more)

### Community 107 - "Community 107"
Cohesion: 0.22
Nodes (8): PlannerOutput, test_normalize_output_adds_task_id_and_sets_status(), test_normalize_output_preserves_task_args(), test_planner_output_accepts_task_missing_fields_when_propagated_top_level(), test_planner_output_accepts_unrelated_query_with_no_tasks(), test_planner_output_allows_task_missing_fields_before_normalization(), test_planner_output_rejects_confidence_out_of_range(), test_planner_output_rejects_multiple_tasks_without_aggregation()

### Community 108 - "Community 108"
Cohesion: 0.25
Nodes (8): conditionToString(), createReadyTimeoutError(), getProcessLogs(), matchPattern(), startProcessCallbackStream(), streamProcessLogs(), waitForLogPattern(), waitForProcessExit()

### Community 109 - "Community 109"
Cohesion: 0.36
Nodes (9): authHeader(), buf2hex(), canonicalString(), hash(), hexBodyHash(), hmac(), sign(), signature() (+1 more)

### Community 110 - "Community 110"
Cohesion: 0.29
Nodes (6): # TODO: Don't understand this code block, why we have this and what is does, # TODO: use the prompt.py only, not build random prompt repair, # TODO: explain why have safe fail ouput, if the planner failed, it should fail, # TODO: Explain this code block, # TODO: if we dont need the build repair prompt, does this code block still usef, # TODO: explain this code block

### Community 111 - "Community 111"
Cohesion: 0.50
Nodes (3): PlannerInvokeRequest, API request for invoking or resuming the planner., _user_input_must_not_be_blank()

### Community 112 - "Community 112"
Cohesion: 0.67
Nodes (3): code:bash (POST /sandbox/{sandbox_id}/exec), code:json ({), Execute Command

## Knowledge Gaps
- **830 isolated node(s):** `PreToolUse`, `name`, `description`, `supportedInterfaces`, `version` (+825 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `command()` connect `Community 104` to `Community 4`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `PlannerService` connect `Community 0` to `Community 33`, `Community 103`, `Community 104`, `Community 73`, `Community 105`, `Community 18`, `Community 84`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `type()` connect `Community 2` to `Community 106`, `Community 4`, `Community 78`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `PlannerService` (e.g. with `FakeGraph` and `FakeInterrupt`) actually correct?**
  _`PlannerService` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `InvoiceAgent` (e.g. with `MCPToolAgent` and `test_invoice_agent_parse_request()`) actually correct?**
  _`InvoiceAgent` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Normalize FastMCP CallToolResult output into plain Python values.      FastMCP c`, `PreToolUse`, `# TODO: Langsmith can not track eventhough i had enabled langsmith tracing` to the rest of the system?**
  _904 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.14623655913978495 - nodes in this community are weakly interconnected._