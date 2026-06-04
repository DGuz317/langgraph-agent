# Multi-Agent System Using LangGraph

## Overview

This project is a Python multi-agent system for invoice and music queries. It uses LangGraph for orchestration, A2A services for domain-agent boundaries, FastMCP tools for database access, LangChain agents for tool-calling behavior, and the Chinook SQLite database as the sample data source.

The current checkpoint has moved past a rule-based demo. The planner produces structured tasks, LangGraph owns routing and same-thread state, invoice and music run as LangChain MCP agents behind A2A services, LangSmith owns execution tracing, and Acontext is used only as an optional skill-learning memory layer.

## Architecture

```text
User input
-> Planner CLI or POST /planner/invoke
-> PlannerService
-> optional Acontext recall
-> checkpointed same-thread messages
-> PlannerAgent structured PlannerOutput
-> LangGraph planner_app
-> natural-language task instruction
-> Invoice/Music A2A service
-> LangChain agent runtime
-> FastMCP database tools
-> internal Aggregator
-> final answer
-> optional Acontext skill learning
```

Core boundaries:

- `planner/` owns the planner prompt, structured `PlannerOutput`, and LLM repair path.
- `planner_app/` owns the LangGraph workflow, checkpointed thread state, domain dispatch, and final response node.
- `orchestrator/` owns `PlannerService`, the FastAPI endpoint, Acontext recall, and Acontext skill-learning capture.
- `a2a_client/` owns JSON-RPC clients for external A2A services.
- `a2a_servers/invoice_agent/` owns the invoice LangChain MCP agent and A2A executor.
- `a2a_servers/music_agent/` owns the music LangChain MCP agent and A2A executor.
- `mcp_server/` owns FastMCP tool registration and Chinook database queries.
- `aggregator/` owns internal final response composition.

## Agent Boundaries

The invoice and music agents are the external domain agents. They are exposed over A2A so other frameworks such as ADK or CrewAI can connect at that boundary.

FastMCP tools are internal tool surfaces for the LangChain domain agents:

- Invoice agent connects to invoice MCP tools.
- Music agent connects to music MCP tools.
- The planner does not call MCP tools directly.
- The aggregator is internal only and is not exposed as an A2A agent.

The planner passes natural-language `task["instruction"]` text to the selected A2A agent. Do not reintroduce planner-side tool names, intent enums, or args builders as the execution contract.

## Current Domain Behavior

Invoice agent capabilities:

- Invoice rows by customer.
- Invoice detail by invoice ID.
- Invoice summary totals by customer.
- Invoice rows sorted by invoice-line unit price.
- Customer support employee lookup.
- Support employee lookup by invoice ID, with optional customer ID validation.
- Read-only invoice database questions through the allowed invoice query tool.

Music agent capabilities:

- Albums by artist.
- Tracks by artist.
- Songs by genre.
- Song existence checks.
- Read-only music database questions through the allowed music query tool.

Current invoice support employee rule:

- Support employee details are included only when the user explicitly asks for them.
- Normal invoice-list queries should return invoice information only.
- Normal invoice-list answers must not add `Support Employee: [Not Available]`.
- If a user later asks for support employee for the same invoices in the same thread, the planner can use same-thread invoice context.
- MCP invoice ID and customer ID arguments accept model-produced strings or integers and are coerced before parameterized SQL execution.
- Freeform read-only invoice SQL returns a controlled error payload for database execution mistakes such as nonexistent columns, while domain/security validation still rejects unsafe or cross-domain queries.

This corrects the older rule that every invoice row should always include support employee data.

## Thread Context And Memory

LangGraph checkpointers preserve short-term state for the same `thread_id`. The planner now receives checkpointed user/assistant messages as real chat history, not only a compressed text summary. This lets the LLM reason over same-thread follow-ups and clarification answers using the same pattern as LangGraph short-term memory.

Current state fields include:

- `messages`: recent user/assistant turns for the same thread.
- `invoice_context`: sanitized invoice follow-up context such as customer ID, recent invoice IDs, and last invoice instruction.
- domain results and final answer values for the current run.

Use the same `thread_id` for normal follow-up messages. The deprecated `resume` API field is ignored for normal conversation; it should only be used again if real LangGraph interrupts are reintroduced.

The planner also stores a small sanitized same-thread invoice context after successful invoice results. The context can include:

- `customer_id`
- recent `invoice_ids`
- the last invoice instruction

This allows follow-up requests such as `Can you provide the support employee for each invoices?` to refer to the previous invoice result without forcing the user to restate invoice IDs.

## Aggregator Behavior

The aggregator remains internal. It has two jobs:

- Format invoice/music domain-agent results into the final answer.
- Generate direct no-task/general replies through the configured LLM.

That means a message such as `Hello, what can you do?` should be handled by the aggregator LLM path, not by hard-coded text in `planner_app/nodes.py`.

## Acontext Skill Learning And LangSmith Tracing

Acontext is optional. When enabled, it stores compact user/assistant outcomes for skill learning and recall. It is not the task-tracking or execution-tracing source for this app.

Current Acontext behavior:

1. Store the real user message.
2. Store the final assistant answer.
3. Disable Acontext task tracking for created sessions.
4. On completed planner responses, flush and submit the session to learning.
5. Fail open if Acontext is unavailable.

Planner execution does not wait on long Acontext task extraction. Acontext recall is also fail-open, so invoice/music requests still complete when the local Acontext API is unavailable.

LangSmith tracing is the execution observability layer. Graph and API calls use explicit run names, tags, and metadata so traces show planner, domain-agent, tool, and aggregation flow without relying on Acontext task extraction.

Acontext references used for this checkpoint:

- https://docs.acontext.io/observe/whatis
- https://docs.acontext.io/observe/agent_tasks
- https://docs.acontext.io/observe/buffer
- https://docs.acontext.io/observe/task_eval_criteria

## Runtime Commands

Install dependencies:

```bash
uv sync
```

Start services in separate terminals:

```bash
uv run python scripts/run_mcp_server.py --host localhost --port 10000 --transport streamable-http
uv run python scripts/run_invoice_a2a.py --host localhost --port 11001
uv run python scripts/run_music_a2a.py --host localhost --port 11002
```

Run the planner CLI:

```bash
uv run python scripts/run_planner.py
```

Run the planner API:

```bash
uv run python scripts/run_orchestrator_api.py --host localhost --port 12000
```

Invoke the planner API:

```http
POST http://localhost:12000/planner/invoke
```

```json
{
  "user_input": "Get 5 most recent invoices",
  "thread_id": "example-thread"
}
```

For normal same-thread follow-ups, keep the same `thread_id` and omit `resume` or set it to `false`:

```json
{
  "user_input": "My customer id is 1",
  "thread_id": "example-thread",
  "resume": false
}
```

## Configuration Notes

- Runtime config loads from `.env` through `src/multi_agent_system/config.py`.
- `SQLITE_DB` has no default and must point at the Chinook SQLite database.
- Default LLM provider is Ollama: `MODEL_PROVIDER=ollama`, `LLM_MODEL=gpt-oss`.
- OpenAI, Google, and Anthropic require their matching API key.
- Acontext is optional and fails open if its local API is unavailable.
- `ACONTEXT_ENABLED=true` enables skill-learning capture.
- `ACONTEXT_RECALL_ENABLED=true` enables recall into planner guidance.
- `ACONTEXT_BASE_URL` defaults to the local Acontext API endpoint.
- LangSmith tracing is configured through the standard LangSmith environment variables.
- `langgraph.json` is empty; use the scripts above instead of assuming LangGraph dev-server config.

## Testing

Run all local tests:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests -q
```

Recent focused verification:

```text
Planner focused tests: 17 passed
Real MCP integration tests: 28 passed
```

Useful focused tests:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_planner_agent.py tests/test_planner_workflow.py -q
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_aggregator.py tests/test_acontext_capture.py -q
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_langchain_domain_agents.py tests/test_a2a_client.py -q
```

Opt-in real-service tests require `.env` and running services:

```bash
RUN_MCP_INTEGRATION_TESTS=1 UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mcp_tools.py -q
RUN_A2A_INTEGRATION_TESTS=1 UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_invoice_a2a_client.py tests/test_music_a2a_client.py -q
RUN_ORCHESTRATOR_API_INTEGRATION_TESTS=1 UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_orchestrator_api_integration.py -q
RUN_ACONTEXT_INTEGRATION_TESTS=1 UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_acontext_capture_integration.py -q
```

## Current Checkpoint

Completed in this checkpoint:

- Planner short-term memory now passes checkpointed same-thread messages into the structured planner LLM as chat history.
- Normal same-thread follow-ups use `thread_id`; `resume` is no longer used for ordinary conversation continuation.
- Invoice support employee behavior is explicit-only.
- Invoice support employee lookup works with invoice ID alone, with optional customer ID validation.
- MCP invoice/customer ID tools tolerate model-produced integers and coerce them before parameterized SQL execution.
- Freeform read-only SQL query tools return controlled database error payloads for execution mistakes.
- General/no-task final responses are handled by the internal aggregator LLM path.
- Acontext capture is reduced to skill-learning outcomes and fails open.
- LangSmith is the tracing layer for planner and agent execution.
- Graphify output was refreshed with `graphify update .`.

## Roadmap

Near-term:

- Validate same-thread customer clarification behavior against the local LLM after the planner message-history change.
- Run a live API smoke for: underspecified invoice request, customer ID follow-up, support employee follow-up.
- Continue removing legacy interrupt/resume assumptions from docs and tests where they no longer match the product flow.

Medium-term:

- Add more music capabilities, such as tracks by album and top tracks by genre.
- Add durable checkpointing for non-demo deployments.
- Consider parallel invoice/music execution after the sequential flow remains stable.

Later:

- Add Docker and compose files for local service orchestration.
- Add service health checks.
- Add production logging/tracing guidance.
- Add CI for `uv run pytest tests -q`.
