# Multi-Agent System Using LangGraph

## Overview

This project is a Python multi-agent system for invoice and music queries. It uses LangGraph for orchestration, A2A services for domain agents, FastMCP tools for database access, and the Chinook SQLite database as the sample data source.

The current implementation is past the initial demo stage. It has a tested planner runtime, CLI and API entrypoints, structured internal task payloads, text-compatible A2A execution, and invoice result enrichment with support employee data.

## Current Architecture

```text
User input
-> Planner CLI or POST /planner/invoke
-> PlannerService
-> PlannerAgent structured PlannerOutput
-> LangGraph planner_app
-> optional HITL interrupt/resume
-> task intent + args
-> build_a2a_payload_from_task()
-> text-compatible A2A instruction
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
- `scripts/run_planner.py` uses `PlannerService` and configurable memory or SQLite checkpointing.
- `src/multi_agent_system/orchestrator/server.py` exposes `POST /planner/invoke`.
- Graph nodes rebuild execution instructions from structured `task["args"]`, not stale planner instruction text.
- `build_a2a_payload_from_task()` creates `{agent, intent, args, instruction}` for every executable task.
- Current A2A compatibility still sends `payload["instruction"]` as text.
- A2A client handles HTTP errors, timeouts, JSON-RPC errors, invalid JSON, missing result objects, and malformed response parts.
- MCP tool agent handles tool loading, missing tools, invocation errors, invalid JSON payloads, and unsupported MCP result shapes.
- Invoice agent supports `latest_invoice`, `all_invoices`, `latest_invoice_support_employee`, and `invoices_by_unit_price`.
- Music agent supports tracks by artist, albums by artist, songs by genre, and song existence checks.

## Current Invoice Rule

Any invoice information returned for a customer must include the support employee for the corresponding invoice.

Current invoice response shapes:

```text
latest_invoice -> {latest_invoice, support_employee}
all_invoices -> [{invoice, support_employee}, ...]
invoices_by_unit_price -> [{invoice, support_employee}, ...]
latest_invoice_support_employee -> {latest_invoice, support_employee}
```

This means a prompt such as `All my invoice information of customer id 5` should return all invoice rows for customer 5 and attach `support_employee` data to each row.

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
```

## Configuration Notes

- Runtime config loads from `.env` through `src/multi_agent_system/config.py`.
- `SQLITE_DB` has no default and must point at the Chinook SQLite database.
- Default LLM provider is Ollama: `MODEL_PROVIDER=ollama`, `LLM_MODEL=gpt-oss`.
- OpenAI, Google, and Anthropic require their matching API key.
- `langgraph.json` is empty; use the scripts above instead of assuming LangGraph dev-server config.

## Roadmap

### Phase 1: Stabilize Current Invoice Behavior

Priority: high.

- Run real-service smoke prompts through `scripts/run_planner.py` and `/planner/invoke`.
- Confirm all invoice prompts return support employee data for each returned invoice row.
- Add regression tests for prompt wording that the LLM planner routes incorrectly.
- Keep `task["args"]` and `a2a_payload` as the compatibility contract.

### Phase 2: Replace Domain Text Parsing With Structured Inputs

Priority: high.

Current services still parse text instructions such as:

```text
Get all invoices for customer_id=5
```

Target internal service contract:

```json
{
  "agent": "invoice",
  "intent": "all_invoices",
  "args": {"customer_id": "5"}
}
```

Implementation notes:

- Add structured request models for invoice and music A2A executors.
- Accept structured payloads first and fall back to text parsing.
- Keep existing text tests until structured transport is fully proven.

### Phase 3: Add Focused Domain Capabilities

Priority: medium.

Invoice candidates:

- invoice detail by `invoice_id`
- customer invoice summary totals
- employee/support lookup by customer without returning invoice rows

Music candidates:

- tracks by album
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
