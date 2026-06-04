import json
import re
from typing import Any

from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient
from multi_agent_system.a2a_client.music_client import MusicA2AClient
from multi_agent_system.aggregator.agent import AggregatorAgent
from multi_agent_system.aggregator.schemas import AggregatorInput, AgentResult
from multi_agent_system.common.execution_evidence import ExecutionEvidence
from multi_agent_system.planner.agent import PlannerAgent
from multi_agent_system.planner_app.state import PlannerAppState


planner = PlannerAgent()
aggregator = AggregatorAgent()


async def planner_node(state: PlannerAppState) -> dict:
    messages = _append_message(
        state.get("messages", []),
        role="user",
        content=state["user_input"],
    )
    invoice_context = _merge_invoice_context(
        state.get("invoice_context"),
        _invoice_context_from_messages(messages),
    )
    memory_context = _planner_memory_context(
        state.get("memory_context"),
        invoice_context,
        messages,
    )
    if memory_context:
        output = await planner.ainvoke(
            state["user_input"],
            memory_context=memory_context,
        )
    else:
        output = await planner.ainvoke(state["user_input"])

    planner_output = _apply_invoice_thread_context(
        output.model_dump(),
        {**state, "invoice_context": invoice_context},
    )
    return {
        "messages": messages,
        "invoice_context": invoice_context,
        "planner_output": planner_output,
        "missing_fields": planner_output.get("missing_fields", []),
        "execution_evidence": _planner_decision_evidence(planner_output),
        "invoice_result": None,
        "music_result": None,
        "final_answer": None,
    }


async def invoice_node(state: PlannerAppState) -> dict:
    planner_output = _copy_planner_output(state)
    task: dict[str, Any] | None = None

    try:
        task = _get_next_task_for_agent(planner_output, agent="invoice")

        result = await InvoiceA2AClient().ask(_task_instruction(task))
        task["status"] = "completed"
        remote_evidence = _extract_remote_evidence(result)

        return {
            "planner_output": planner_output,
            "invoice_result": result,
            "invoice_context": _invoice_context_from_result(
                result,
                state=state,
                task=task,
                evidence=remote_evidence,
            ) or state.get("invoice_context", {}),
            "execution_evidence": _with_evidence(
                state,
                _dispatch_evidence(task),
                *remote_evidence,
                _agent_result_evidence("invoice", completed=True),
            ),
        }

    except (ValueError, TimeoutError, ConnectionError, RuntimeError) as exc:
        _mark_task_failed(task)

        return {
            "planner_output": planner_output,
            "invoice_result": _failure_result("Invoice", exc),
            "execution_evidence": _with_evidence(
                state,
                *([_dispatch_evidence(task)] if task is not None else []),
                _agent_result_evidence("invoice", completed=False),
            ),
        }


async def music_node(state: PlannerAppState) -> dict:
    planner_output = _copy_planner_output(state)
    task: dict[str, Any] | None = None

    try:
        task = _get_next_task_for_agent(planner_output, agent="music")

        result = await MusicA2AClient().ask(_task_instruction(task))
        task["status"] = "completed"

        return {
            "planner_output": planner_output,
            "music_result": result,
            "execution_evidence": _with_evidence(
                state,
                _dispatch_evidence(task),
                *_extract_remote_evidence(result),
                _agent_result_evidence("music", completed=True),
            ),
        }

    except (ValueError, TimeoutError, ConnectionError, RuntimeError) as exc:
        _mark_task_failed(task)

        return {
            "planner_output": planner_output,
            "music_result": _failure_result("Music", exc),
            "execution_evidence": _with_evidence(
                state,
                *([_dispatch_evidence(task)] if task is not None else []),
                _agent_result_evidence("music", completed=False),
            ),
        }


async def final_response_node(state: PlannerAppState) -> dict:
    invoice_result = state.get("invoice_result")
    music_result = state.get("music_result")

    results: list[AgentResult] = []

    if invoice_result:
        results.append(
            AgentResult(
                agent="invoice_agent",
                result=invoice_result,
            )
        )

    if music_result:
        results.append(
            AgentResult(
                agent="music_agent",
                result=music_result,
            )
        )

    user_input = _response_user_input(state)
    output = await aggregator.ainvoke(
        AggregatorInput(
            user_input=user_input,
            results=results,
        )
    )
    messages = _append_message(
        state.get("messages", []),
        role="assistant",
        content=output.final_answer,
    )

    return {
        "messages": messages,
        "final_answer": output.final_answer,
        "execution_evidence": _with_evidence(
            state,
            ExecutionEvidence(
                kind="aggregation",
                agent="aggregator",
                operation="final_response" if results else "general_response",
                status="completed",
                summary=(
                    "Combined completed workflow results; returned values omitted from memory."
                    if results
                    else "Generated direct response without domain agent results."
                ),
            ),
        ),
    }


def _copy_planner_output(state: PlannerAppState) -> dict[str, Any]:
    planner_output = dict(state.get("planner_output", {}))

    planner_output["tasks"] = [
        dict(task)
        for task in planner_output.get("tasks", [])
    ]

    return planner_output


def _get_next_task_for_agent(
    planner_output: dict[str, Any],
    agent: str,
) -> dict[str, Any]:
    for task in planner_output.get("tasks", []):
        if (
            task.get("agent") == agent
            and task.get("status", "not_started") == "not_started"
        ):
            return task

    raise ValueError(f"No pending task found for agent: {agent}")


def _task_instruction(task: dict[str, Any]) -> str:
    instruction = str(task.get("instruction") or "").strip()
    if not instruction:
        raise ValueError("Planner task is missing an instruction.")
    return instruction


def _mark_task_failed(task: dict[str, Any] | None) -> None:
    if task is not None:
        task["status"] = "failed"


def _failure_result(agent_label: str, exc: Exception) -> str:
    return f"{agent_label} task failed: {exc}"


def _planner_memory_context(
    memory_context: str | None,
    invoice_context: dict[str, Any] | None,
    messages: list[dict[str, str]] | None = None,
) -> str | None:
    parts = [memory_context.strip()] if memory_context and memory_context.strip() else []
    conversation_context = _format_recent_messages(messages)
    if conversation_context:
        parts.append(
            "Recent same-thread conversation:\n"
            f"{conversation_context}\n"
            "Use this only to resolve direct follow-up references in the current message."
        )
    formatted_invoice_context = _format_invoice_context(invoice_context)
    if formatted_invoice_context:
        parts.append(
            "Recent same-thread invoice context for follow-up references:\n"
            f"{formatted_invoice_context}\n"
            "Use it only when the current user clearly refers to previous invoices."
        )
    return "\n\n".join(parts) if parts else None


def _apply_invoice_thread_context(
    planner_output: dict[str, Any],
    state: PlannerAppState,
) -> dict[str, Any]:
    invoice_context = state.get("invoice_context")
    formatted_context = _format_invoice_context(invoice_context)
    if not formatted_context:
        return planner_output

    updated = dict(planner_output)
    tasks: list[dict[str, Any]] = []
    user_input = str(state.get("user_input") or "")

    for raw_task in updated.get("tasks", []):
        if not isinstance(raw_task, dict):
            continue

        task = dict(raw_task)
        instruction = str(task.get("instruction") or "")
        if (
            task.get("agent") == "invoice"
            and _should_attach_invoice_context(user_input, instruction)
            and "Previous same-thread invoice context:" not in instruction
        ):
            task["instruction"] = (
                f"{instruction.strip()} "
                f"Previous same-thread invoice context: {formatted_context}."
            ).strip()
        tasks.append(task)

    updated["tasks"] = tasks
    return updated


def _should_attach_invoice_context(user_input: str, instruction: str) -> bool:
    combined = f"{user_input} {instruction}".lower()
    if not any(term in combined for term in ("support employee", "support rep")):
        return False

    has_customer_id = _has_labeled_number(combined, ("customer_id", "customer id"))
    has_invoice_id = _has_labeled_number(combined, ("invoice_id", "invoice id"))
    if has_customer_id and has_invoice_id:
        return False

    followup_markers = (
        "each invoice",
        "each invoices",
        "these invoice",
        "these invoices",
        "those invoice",
        "those invoices",
        "previous invoice",
        "previous invoices",
        "this invoice",
        "this invoices",
        "current invoice",
        "current invoices",
        "for them",
        "for each",
        "for this",
    )
    return any(marker in combined for marker in followup_markers)


def _has_labeled_number(text: str, labels: tuple[str, ...]) -> bool:
    return any(
        re.search(
            rf"\b{re.escape(label)}\s*(?:=|:|is)?\s*\d+\b",
            text,
            flags=re.IGNORECASE,
        )
        for label in labels
    )


def _invoice_context_from_result(
    result: str,
    *,
    state: PlannerAppState,
    task: dict[str, Any],
    evidence: list[ExecutionEvidence],
) -> dict[str, Any]:
    parsed = _parse_json_object(result)
    if parsed.get("success") is False:
        return {}

    content = str(parsed.get("content") or "")
    data = parsed.get("data")
    prior_context = state.get("invoice_context")
    customer_id = (
        _first_text_value(state.get("customer_id"))
        or _customer_id_from_evidence(evidence)
        or _customer_id_from_data(data)
        or _customer_id_from_text(content)
        or _customer_id_from_text(str(task.get("instruction") or ""))
        or (
            _first_text_value(prior_context.get("customer_id"))
            if isinstance(prior_context, dict)
            else None
        )
    )
    invoice_ids = _invoice_ids_from_data(data) or _invoice_ids_from_text(content)
    if not invoice_ids and isinstance(prior_context, dict):
        prior_invoice_ids = prior_context.get("invoice_ids")
        if isinstance(prior_invoice_ids, list):
            invoice_ids = [
                str(value).strip()
                for value in prior_invoice_ids
                if str(value).strip()
            ]

    context: dict[str, Any] = {}
    if customer_id:
        context["customer_id"] = customer_id
    if invoice_ids:
        context["invoice_ids"] = invoice_ids[:10]

    instruction = str(task.get("instruction") or "").strip()
    if instruction:
        context["last_invoice_instruction"] = instruction
    return context


def _invoice_context_from_messages(
    messages: list[dict[str, str]] | None,
) -> dict[str, Any]:
    text = "\n".join(
        str(message.get("content") or "")
        for message in (messages or [])
        if str(message.get("content") or "")
    )
    customer_id = _customer_id_from_text(text)
    invoice_ids = _invoice_ids_from_text(text)

    context: dict[str, Any] = {}
    if customer_id:
        context["customer_id"] = customer_id
    if invoice_ids:
        context["invoice_ids"] = invoice_ids[:10]
    return context


def _merge_invoice_context(
    current: dict[str, Any] | None,
    discovered: dict[str, Any] | None,
) -> dict[str, Any]:
    merged: dict[str, Any] = dict(current or {})

    for key in ("customer_id", "last_invoice_instruction"):
        value = _first_text_value((discovered or {}).get(key))
        if value:
            merged[key] = value

    discovered_ids = (discovered or {}).get("invoice_ids")
    if isinstance(discovered_ids, list) and discovered_ids:
        merged["invoice_ids"] = [
            str(value).strip()
            for value in discovered_ids
            if str(value).strip()
        ][:10]

    return merged


def _parse_json_object(value: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return {}

    return parsed if isinstance(parsed, dict) else {}


def _customer_id_from_evidence(evidence: list[ExecutionEvidence]) -> str | None:
    for item in evidence:
        value = item.arguments.get("customer_id")
        cleaned = _first_text_value(value)
        if cleaned:
            return cleaned
    return None


def _customer_id_from_data(data: Any) -> str | None:
    rows = data if isinstance(data, list) else [data]
    for row in rows:
        if isinstance(row, dict):
            value = row.get("CustomerId") or row.get("customer_id")
            cleaned = _first_text_value(value)
            if cleaned:
                return cleaned
    return None


def _customer_id_from_text(text: str) -> str | None:
    matches = re.findall(
        r"\b(?:customer_id|customer id|customerID|customerId)\s*(?:=|:|is)?\s*(\d+)\b",
        text,
        flags=re.IGNORECASE,
    )
    return matches[-1] if matches else None


def _invoice_ids_from_data(data: Any) -> list[str]:
    rows = data if isinstance(data, list) else [data]
    values: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        value = row.get("InvoiceId") or row.get("invoice_id")
        cleaned = _first_text_value(value)
        if cleaned and cleaned not in values:
            values.append(cleaned)
    return values


def _invoice_ids_from_text(text: str) -> list[str]:
    values: list[str] = []
    patterns = (
        r"\bInvoice ID:\s*(\d+)\b",
        r"\bInvoiceId['\"]?\s*[:=]\s*(\d+)\b",
        r"\bInvoiceId\W*[:=]\W*(\d+)\b",
    )
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            if match not in values:
                values.append(match)
    return values


def _first_text_value(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    return text or None


def _format_invoice_context(invoice_context: dict[str, Any] | None) -> str:
    if not isinstance(invoice_context, dict) or not invoice_context:
        return ""

    parts: list[str] = []
    customer_id = _first_text_value(invoice_context.get("customer_id"))
    if customer_id:
        parts.append(f"customer_id={customer_id}")

    invoice_ids = invoice_context.get("invoice_ids")
    if isinstance(invoice_ids, list):
        cleaned_ids = [
            str(value).strip()
            for value in invoice_ids
            if str(value).strip()
        ]
        if cleaned_ids:
            parts.append(f"invoice_ids={', '.join(cleaned_ids[:10])}")

    instruction = _first_text_value(invoice_context.get("last_invoice_instruction"))
    if instruction:
        parts.append(f"last_invoice_instruction={instruction}")

    return "; ".join(parts)


def _response_user_input(state: PlannerAppState) -> str:
    missing_fields = state.get("missing_fields", [])
    if not missing_fields:
        return state["user_input"]

    return (
        f"Current user message: {state['user_input']}\n"
        f"Planner needs more information before routing: {', '.join(missing_fields)}.\n"
        "Ask the user one concise follow-up question. Do not claim that tools were called."
    )


def _append_message(
    messages: list[dict[str, str]] | None,
    *,
    role: str,
    content: str,
    limit: int = 12,
) -> list[dict[str, str]]:
    updated = [
        {"role": str(message.get("role") or ""), "content": str(message.get("content") or "")}
        for message in (messages or [])
        if str(message.get("role") or "") and str(message.get("content") or "")
    ]
    updated.append({"role": role, "content": content})
    return updated[-limit:]


def _format_recent_messages(
    messages: list[dict[str, str]] | None,
    *,
    max_messages: int = 6,
    max_chars: int = 1600,
) -> str:
    lines: list[str] = []
    for message in (messages or [])[-max_messages:]:
        role = str(message.get("role") or "").strip()
        content = " ".join(str(message.get("content") or "").split())
        if not role or not content:
            continue
        lines.append(f"{role}: {content}")

    text = "\n".join(lines)
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def _planner_decision_evidence(planner_output: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = planner_output.get("tasks", [])
    if not tasks:
        return [
            ExecutionEvidence(
                kind="planner_decision",
                agent="planner",
                operation="no_task",
                status="completed",
                summary="Planner found no executable invoice or music workflow.",
            ).model_dump()
        ]

    evidence: list[dict[str, Any]] = []
    for task in tasks:
        missing_fields = [str(field) for field in task.get("missing_fields", [])]
        if missing_fields:
            summary = "Planner selected a workflow requiring additional fields."
        else:
            summary = "Planner selected an executable agent dispatch."
        evidence.append(
            ExecutionEvidence(
                kind="planner_decision",
                agent="planner",
                operation=str(task.get("agent", "unknown")),
                status="interrupted" if missing_fields else "completed",
                fields=missing_fields,
                summary=summary,
            ).model_dump()
        )
    return evidence


def _with_evidence(
    state: PlannerAppState,
    *new_evidence: ExecutionEvidence,
) -> list[dict[str, Any]]:
    return [
        *state.get("execution_evidence", []),
        *(item.model_dump() for item in new_evidence),
    ]


def _dispatch_evidence(task: dict[str, Any]) -> ExecutionEvidence:
    return ExecutionEvidence(
        kind="a2a_dispatch",
        agent=task["agent"],
        operation="agent_instruction",
        status="started",
        summary="Dispatched natural-language instruction to domain agent.",
    )


def _agent_result_evidence(
    agent: str,
    *,
    completed: bool,
) -> ExecutionEvidence:
    return ExecutionEvidence(
        kind="agent_result",
        agent=agent,
        operation="agent_instruction",
        status="completed" if completed else "failed",
        summary=(
            "Domain agent completed the instruction."
            if completed
            else "Domain agent failed the instruction."
        ),
    )


def _extract_remote_evidence(result: str) -> list[ExecutionEvidence]:
    try:
        parsed = json.loads(result)
    except (TypeError, json.JSONDecodeError):
        return []

    if not isinstance(parsed, dict):
        return []

    evidence: list[ExecutionEvidence] = []
    for value in parsed.get("execution_evidence", []):
        try:
            evidence.append(ExecutionEvidence.model_validate(value))
        except ValueError:
            continue
    return evidence
