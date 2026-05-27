# Multi-Agent System Using LangGraph

## Overview

This project is a Python multi-agent system for invoice and music queries. It uses LangGraph for orchestration, A2A services for domain agents, FastMCP tools for database access, and the Chinook SQLite database as the sample data source.

The current implementation is past the initial demo stage. It has a tested planner runtime, CLI and API entrypoints, structured internal task payloads, structured-first A2A execution with text fallback, and invoice result enrichment with support employee data.

## Current Architecture

```text
User input
-> Planner CLI or POST /planner/invoke
-> PlannerService
-> optional Acontext sanitized execution-evidence capture and skill learning
-> PlannerAgent structured PlannerOutput
-> LangGraph planner_app
-> optional HITL interrupt/resume
-> task intent + args
-> build_a2a_payload_from_task()
-> A2A structured data part plus compatibility text instruction
-> Invoice/Music A2A service
-> MCP tools
-> Aggregator
-> final answer
```

## Core Boundaries

- `planner/` owns LLM planning, prompts, and structured task schemas.
- `planner_app/` owns LangGraph nodes, edges, HITL, task execution, and final response flow.
- `orchestrator/` owns the reusable `PlannerService` and FastAPI planner endpoint.
- `a2a_client/` owns reusable JSON-RPC clients for A2A services.
- `a2a_servers/invoice_agent/` owns invoice domain parsing and invoice MCP tool orchestration.
- `a2a_servers/music_agent/` owns music domain parsing and music MCP tool orchestration.
- `mcp_server/` owns database access and tool registration.
- `aggregator/` owns final user-facing formatting.

## Current Checkpoint

Completed:

- Planner schema validates agent/intent compatibility, required args or missing fields, confidence range, blank instructions, and aggregation consistency.
- Planner retries invalid structured LLM output once before returning a safe failed output.
- Planner structured LLM initialization is lazy for easier unit testing.
- `PlannerService` wraps graph invocation, thread ids, HITL resume, interrupt extraction, and final-answer extraction.
- Optional Acontext capture records sanitized workflow decisions, domain dispatch, and MCP outcome summaries in a shared learning space and flushes terminal sessions for skill generation.
- `scripts/run_planner.py` uses `PlannerService` and configurable memory or SQLite checkpointing.
- `src/multi_agent_system/orchestrator/server.py` exposes `POST /planner/invoke`.
- Graph nodes rebuild execution instructions from structured `task["args"]`, not stale planner instruction text.
- `build_a2a_payload_from_task()` creates `{agent, intent, args, instruction}` for every executable task.
- Planner task execution sends `a2a_payload` as native A2A structured data and retains `payload["instruction"]` as a text compatibility part.
- Invoice and music A2A executors validate structured requests first and fall back to legacy text-only callers.
- Planner graph callbacks are asynchronous so API/CLI `ainvoke()` flows do not depend on thread-dispatched callbacks.
- A2A client handles HTTP errors, timeouts, JSON-RPC errors, invalid JSON, missing result objects, and malformed response parts.
- MCP tool agent handles tool loading, missing tools, invocation errors, invalid JSON payloads, and unsupported MCP result shapes.
- Invoice agent supports `latest_invoice`, `invoice_detail`, `invoice_summary`, `customer_support_employee`, `all_invoices`, `latest_invoice_support_employee`, and `invoices_by_unit_price`.
- Invoice MCP lookups use parameterized identifier queries, including summary totals and existing invoice/employee paths.
- Music agent supports tracks by artist, albums by artist, songs by genre, and song existence checks.

## Current Invoice Rule

Any returned invoice information must include the support employee for the corresponding invoice.

Current invoice response shapes:

```text
latest_invoice -> {latest_invoice, support_employee}
invoice_detail -> {invoice, support_employee}
all_invoices -> [{invoice, support_employee}, ...]
invoices_by_unit_price -> [{invoice, support_employee}, ...]
latest_invoice_support_employee -> {latest_invoice, support_employee}
invoice_summary -> {CustomerId, InvoiceCount, TotalAmount}
customer_support_employee -> {support_employee}
```

This means a prompt such as `All my invoice information of customer id 5` should return all invoice rows for customer 5 and attach `support_employee` data to each row.
Summary requests return aggregate totals only and therefore do not return invoice rows requiring enrichment. Direct customer support lookup returns only the assigned `support_employee` and does not retrieve invoice rows.

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

Optional local skill memory:

```bash
# Acontext SDK API endpoint, distinct from the sandbox worker on port 8788.
curl -fsS http://localhost:8029/health
```

Set `ACONTEXT_ENABLED=true`, `ACONTEXT_API_KEY`, and
`ACONTEXT_BASE_URL=http://localhost:8029/api/v1` to capture sanitized planner
workflow evidence. Captured memory excludes raw user-entered values and
invoice/music result payloads. The current memory phase generates reviewable
skills; it does not yet inject those skills back into planning. The local
learning setup uses an Ollama container reachable by the Acontext containers;
for slow local models, set `ACONTEXT_TIMEOUT=1000` so terminal flush
processing can finish. Sanitized capture writes to the new
`sanitized-execution-v1` memory scope rather than reusing prior raw
`visible-chat-v1` learning sessions.

Invoke the planner API:

```http
POST http://localhost:12000/planner/invoke
```

```json
{
  "user_input": "All my invoice information of customer id 5",
  "thread_id": null,
  "resume": false
}
```

## Test Commands

Run all local tests:

```bash
uv run pytest tests -q
```

Run focused invoice enrichment checks:

```bash
uv run pytest tests/test_invoice_agent_parsing.py tests/test_invoice_support_employee_integration.py tests/test_planner_e2e_flows.py -q
```

Run opt-in real-service tests after configuring `.env` and starting MCP plus A2A services:

```bash
RUN_INVOICE_SUPPORT_INTEGRATION_TESTS=1 uv run pytest tests/test_invoice_support_employee_integration.py -q
RUN_A2A_PAYLOAD_INTEGRATION_TESTS=1 uv run pytest tests/test_a2a_payload_integration.py -q
RUN_ORCHESTRATOR_API_INTEGRATION_TESTS=1 uv run pytest tests/test_orchestrator_api_integration.py -q
RUN_A2A_INTEGRATION_TESTS=1 uv run pytest tests/test_invoice_a2a_client.py tests/test_music_a2a_client.py -q
RUN_MCP_INTEGRATION_TESTS=1 uv run pytest tests/test_mcp_tools.py -q
RUN_LLM_TESTS=1 uv run pytest tests/test_llm_planner.py -q
RUN_ACONTEXT_INTEGRATION_TESTS=1 uv run pytest tests/test_acontext_capture_integration.py -q
```

## Configuration Notes

- Runtime config loads from `.env` through `src/multi_agent_system/config.py`.
- `SQLITE_DB` has no default and must point at the Chinook SQLite database.
- Default LLM provider is Ollama: `MODEL_PROVIDER=ollama`, `LLM_MODEL=gpt-oss`.
- OpenAI, Google, and Anthropic require their matching API key.
- Acontext is optional and fails open if its local API is unavailable; its SDK API defaults to port `8029`, not the sandbox worker on `8788`.
- `langgraph.json` is empty; use the scripts above instead of assuming LangGraph dev-server config.

## Roadmap

### Phase 1: Stabilize Current Invoice Behavior

Priority: high.

- Completed in automated coverage: invoice response-shape tests verify support employee enrichment for latest, all, and unit-price-sorted invoice flows.
- Completed live validation on May 26, 2026: `scripts/run_planner.py` and the focused `/planner/invoke` integration flow completed through local Ollama `gpt-oss`, A2A, MCP, and Chinook.
- Keep `task["args"]` and `a2a_payload` as the execution contract.

### Phase 2: Replace Domain Text Parsing With Structured Inputs

Priority: high.

Implemented transport contract:

```text
Get all invoices for customer_id=5
```

```json
{
  "agent": "invoice",
  "intent": "all_invoices",
  "args": {"customer_id": "5"},
  "instruction": "Get all invoices for customer_id=5"
}
```

- Planner nodes send this payload in an A2A data part and include `instruction` as a text part for compatibility.
- Invoice and music executors dispatch typed structured requests when supplied and retain text parsing for direct legacy callers.
- Existing text A2A tests remain as backward-compatibility coverage.

### Phase 3: Add Focused Domain Capabilities

Priority: medium.

Invoice candidates:

- Implemented: invoice detail by `invoice_id`, including support employee enrichment.
- Implemented: customer invoice summary totals by `customer_id`.
- Implemented: employee/support lookup by `customer_id` without returning invoice rows.

Music candidates:

- Next: tracks by album
- top tracks by genre
- playlist-style recommendations with limits

Add each capability through the full stack: schema, prompt, task instruction or payload, agent path, MCP tool, unit tests, and opt-in real-service tests.

### Phase 4: Parallel Multi-Agent Execution

Priority: medium/low.

Current multi-agent flow is sequential:

```text
invoice -> music -> final_response
```

Future flow:

```text
invoice -\
          -> aggregator
music   -/
```

Do this only after structured task payloads replace most domain text parsing, because parallel state merging is harder to debug.

### Phase 5: Deployment Readiness

Priority: later.

- Add `Dockerfile` and `docker-compose.yml`.
- Clean `.env.example` for local and deployed runs.
- Add health-check endpoints.
- Add logging configuration.
- Add LangSmith tracing toggle guidance.
- Add CI that runs `uv run pytest tests -q`.
