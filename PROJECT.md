# Multi-Agent System Using LangGraph

## Overview

This project is a Python multi-agent system for invoice and music queries. It uses LangGraph for orchestration, A2A services for domain-agent boundaries, FastMCP tools for database access, LangChain agents for tool-calling behavior, and the Chinook SQLite database as the sample data source.

The current checkpoint has moved past a rule-based demo. The planner produces structured tasks, LangGraph owns routing and human-in-the-loop control, invoice and music run as LangChain MCP agents behind A2A services, and Acontext observes completed workflows for task tracking and reusable memory.

## Architecture

```text
User input
-> Planner CLI or POST /planner/invoke
-> PlannerService
-> optional Acontext recall
-> PlannerAgent structured PlannerOutput
-> LangGraph planner_app
-> optional HITL interrupt/resume
-> natural-language task instruction
-> Invoice/Music A2A service
-> LangChain agent runtime
-> FastMCP database tools
-> internal Aggregator
-> final answer
-> optional Acontext capture/task tracking
```

Core boundaries:

- `planner/` owns the planner prompt, structured `PlannerOutput`, and LLM repair path.
- `planner_app/` owns the LangGraph workflow, HITL, thread state, domain dispatch, and final response node.
- `orchestrator/` owns `PlannerService`, the FastAPI endpoint, Acontext recall, and Acontext capture.
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
- Support employee for invoice/customer questions.
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

This corrects the older rule that every invoice row should always include support employee data.

## HITL And Thread Context

Human-in-the-loop interrupts are used when critical information is missing and the task cannot be executed safely.

Critical fields currently guarded:

- `customer_id`
- `invoice_id`
- `music_search_type`
- `artist`
- `genre`
- `song_title`

Interrupted runs preserve the LangGraph `thread_id` and resume with `Command(resume=...)`.

The planner also stores a small sanitized same-thread invoice context after successful invoice results. The context can include:

- `customer_id`
- recent `invoice_ids`
- the last invoice instruction

This allows follow-up requests such as `Can you provide the support employee for each invoices?` to refer to the previous invoice result without forcing the user to restate the customer ID.

## Aggregator Behavior

The aggregator remains internal. It has two jobs:

- Format invoice/music domain-agent results into the final answer.
- Generate direct no-task/general replies through the configured LLM.

That means a message such as `Hello, what can you do?` should be handled by the aggregator LLM path, not by hard-coded text in `planner_app/nodes.py`.

## Acontext Capture And Task Tracking

Acontext is optional. When enabled, it observes planner interactions and can learn reusable memory from completed workflows.

The current capture flow follows Acontext task-tracking behavior:

1. Store the real user message as a user message.
2. Store planner decisions and workflow progress as assistant messages.
3. Store MCP tool calls as OpenAI-style assistant tool calls.
4. Store MCP tool results as OpenAI-style tool messages.
5. Store the final assistant answer.
6. On terminal planner responses, call `flush(session_id)`.
7. Poll `messages_observing_status(session_id)`.
8. Check `get_tasks(session_id)` after observing has had a chance to process messages.

Synthetic task-hint user messages were removed. Acontext treats distinct user requests as tasks, so workflow progress should be assistant/tool progress within the real user task, not a fake user request.

If Acontext flush fails, planner execution still succeeds. Capture logs a warning and skips task verification for that interaction.

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

If the response is interrupted, resume the same thread:

```json
{
  "user_input": "My customer id is 1",
  "thread_id": "example-thread",
  "resume": true
}
```

## Configuration Notes

- Runtime config loads from `.env` through `src/multi_agent_system/config.py`.
- `SQLITE_DB` has no default and must point at the Chinook SQLite database.
- Default LLM provider is Ollama: `MODEL_PROVIDER=ollama`, `LLM_MODEL=gpt-oss`.
- OpenAI, Google, and Anthropic require their matching API key.
- Acontext is optional and fails open if its local API is unavailable.
- `ACONTEXT_ENABLED=true` enables capture.
- `ACONTEXT_RECALL_ENABLED=true` enables recall into planner guidance.
- `ACONTEXT_BASE_URL` defaults to the local Acontext API endpoint.
- `langgraph.json` is empty; use the scripts above instead of assuming LangGraph dev-server config.

## Testing

Run all local tests:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests -q
```

Current checkpoint result:

```text
135 passed, 41 skipped
```

Useful focused tests:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_planner_hitl.py tests/test_planner_workflow.py -q
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

- Required MCP tool args are normalized to strings and validated before FastMCP receives a tool call.
- Missing `customer_id=None` no longer reaches invoice MCP tools.
- HITL deterministically detects missing critical invoice/music fields before dispatch.
- Resume answers are rechecked; unresolved critical fields interrupt again instead of being blindly cleared.
- Duplicate and scratch tests were consolidated.
- Invoice support employee behavior changed to explicit-only.
- General/no-task final responses moved into the internal aggregator LLM path.
- Same-thread invoice context was added for support-employee follow-up requests.
- Acontext capture now uses real user messages plus assistant/tool progress and observes flush status before task checks.
- Graphify output was refreshed with `graphify update .`.

Staged code currently leaves unrelated local changes to `src/multi_agent_system/config.py` and `uv.lock` unstaged.

## Roadmap

Near-term:

- Validate the explicit support-employee flow against real MCP and A2A services.
- Confirm Acontext dashboard task extraction for interrupted/resumed planner threads.
- Decide whether to remove legacy support-employee integration tests that assume always-on enrichment.

Medium-term:

- Add more music capabilities, such as tracks by album and top tracks by genre.
- Add durable checkpointing for non-demo deployments.
- Consider parallel invoice/music execution after the sequential flow remains stable.

Later:

- Add Docker and compose files for local service orchestration.
- Add service health checks.
- Add production logging/tracing guidance.
- Add CI for `uv run pytest tests -q`.
