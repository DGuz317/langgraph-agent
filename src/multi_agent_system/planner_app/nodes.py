import json
from typing import Any

from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient
from multi_agent_system.a2a_client.music_client import MusicA2AClient
from multi_agent_system.aggregator.agent import AggregatorAgent
from multi_agent_system.aggregator.schemas import AggregatorInput, AgentResult
from multi_agent_system.common.execution_evidence import ExecutionEvidence
from multi_agent_system.planner.agent import PlannerAgent
from multi_agent_system.planner_app.hitl import interrupt_for_missing_info
from multi_agent_system.planner_app.state import PlannerAppState
from multi_agent_system.planner_app.task_instructions import (
    TaskInstructionError,
    build_a2a_payload_from_task,
)


planner = PlannerAgent()
aggregator = AggregatorAgent()


async def planner_node(state: PlannerAppState) -> dict:
    output = await planner.ainvoke(state["user_input"])

    return {
        "planner_output": output.model_dump(),
        "missing_fields": output.missing_fields,
        "execution_evidence": _planner_decision_evidence(output.model_dump()),
    }


async def missing_info_node(state: PlannerAppState) -> dict:
    missing_fields = state.get("missing_fields", [])
    extracted = interrupt_for_missing_info(missing_fields)

    planner_output = _copy_planner_output(state)
    tasks = planner_output.get("tasks", [])

    for task in tasks:
        if task["agent"] == "invoice" and extracted.get("invoice_id"):
            task["args"] = {"invoice_id": extracted["invoice_id"]}
            _attach_a2a_payload(task)
            task["missing_fields"] = []
            continue

        if task["agent"] == "invoice" and extracted.get("customer_id"):
            task["args"] = {"customer_id": extracted["customer_id"]}
            _attach_a2a_payload(task)
            task["missing_fields"] = []
            continue

        if task["agent"] == "music" and extracted.get("artist"):
            task["intent"] = "tracks_by_artist"
            task["args"] = {"artist": extracted["artist"]}
            _attach_a2a_payload(task)
            task["missing_fields"] = []
            continue

        if task["agent"] == "music" and extracted.get("genre"):
            task["intent"] = "songs_by_genre"
            task["args"] = {"genre": extracted["genre"]}
            _attach_a2a_payload(task)
            task["missing_fields"] = []
            continue

        if task["agent"] == "music" and extracted.get("song_title"):
            task["intent"] = "check_song"
            task["args"] = {"song_title": extracted["song_title"]}
            _attach_a2a_payload(task)
            task["missing_fields"] = []
            continue

    return {
        **extracted,
        "planner_output": planner_output,
        "missing_fields": [],
        "execution_evidence": _with_evidence(
            state,
            ExecutionEvidence(
                kind="hitl_resume",
                agent="planner",
                operation="required_fields",
                status="completed",
                fields=sorted(extracted),
                summary="Required fields were supplied; values omitted from memory.",
            ),
        ),
    }


async def invoice_node(state: PlannerAppState) -> dict:
    planner_output = _copy_planner_output(state)
    task: dict[str, Any] | None = None

    try:
        task = _get_next_task_for_agent(planner_output, agent="invoice")

        payload = _attach_a2a_payload(task)

        result = await InvoiceA2AClient().ask_payload(payload)
        task["status"] = "completed"

        return {
            "planner_output": planner_output,
            "invoice_result": result,
            "execution_evidence": _with_evidence(
                state,
                _dispatch_evidence(task),
                *_extract_remote_evidence(result),
                _agent_result_evidence("invoice", task["intent"], completed=True),
            ),
        }

    except (
        TaskInstructionError,
        ValueError,
        TimeoutError,
        ConnectionError,
        RuntimeError,
    ) as exc:
        _mark_task_failed(task)

        return {
            "planner_output": planner_output,
            "invoice_result": _failure_result("Invoice", exc),
            "execution_evidence": _with_evidence(
                state,
                *([_dispatch_evidence(task)] if task is not None else []),
                _agent_result_evidence(
                    "invoice",
                    str(task.get("intent", "unknown")) if task is not None else "unknown",
                    completed=False,
                ),
            ),
        }


async def music_node(state: PlannerAppState) -> dict:
    planner_output = _copy_planner_output(state)
    task: dict[str, Any] | None = None

    try:
        task = _get_next_task_for_agent(planner_output, agent="music")

        payload = _attach_a2a_payload(task)

        result = await MusicA2AClient().ask_payload(payload)
        task["status"] = "completed"

        return {
            "planner_output": planner_output,
            "music_result": result,
            "execution_evidence": _with_evidence(
                state,
                _dispatch_evidence(task),
                *_extract_remote_evidence(result),
                _agent_result_evidence("music", task["intent"], completed=True),
            ),
        }

    except (
        TaskInstructionError,
        ValueError,
        TimeoutError,
        ConnectionError,
        RuntimeError,
    ) as exc:
        _mark_task_failed(task)

        return {
            "planner_output": planner_output,
            "music_result": _failure_result("Music", exc),
            "execution_evidence": _with_evidence(
                state,
                *([_dispatch_evidence(task)] if task is not None else []),
                _agent_result_evidence(
                    "music",
                    str(task.get("intent", "unknown")) if task is not None else "unknown",
                    completed=False,
                ),
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

    if not results:
        planner_output = state.get("planner_output", {})
        tasks = planner_output.get("tasks", [])

        if not tasks:
            return {
                "final_answer": (
                    "I can help with invoice and music tasks.\n\n"
                    "Examples:\n"
                    "- Get latest invoice for customer_id=5\n"
                    "- Get invoice detail for invoice_id=361\n"
                    "- Get invoice summary for customer_id=5\n"
                    "- Get support employee for customer_id=5\n"
                    "- Show invoices sorted by unit price for customer_id=5\n"
                    "- Find tracks by artist AC/DC\n"
                    "- Recommend songs by genre rock\n"
                    "- Check for song Ligia\n\n"
                    "For vague music requests like 'recommend some songs', "
                    "I will ask whether you want to search by artist or by genre."
                ),
                "execution_evidence": _with_evidence(
                    state,
                    ExecutionEvidence(
                        kind="aggregation",
                        agent="aggregator",
                        operation="capabilities",
                        status="completed",
                        summary="Returned supported workflow guidance.",
                    ),
                ),
            }

        return {
            "final_answer": "I could not complete the request.",
            "execution_evidence": _with_evidence(
                state,
                ExecutionEvidence(
                    kind="aggregation",
                    agent="aggregator",
                    operation="final_response",
                    status="failed",
                    summary="No workflow result was available.",
                ),
            ),
        }

    output = aggregator.invoke(
        AggregatorInput(
            user_input=state["user_input"],
            results=results,
        )
    )

    return {
        "final_answer": output.final_answer,
        "execution_evidence": _with_evidence(
            state,
            ExecutionEvidence(
                kind="aggregation",
                agent="aggregator",
                operation="final_response",
                status="completed",
                summary="Combined completed workflow results; returned values omitted from memory.",
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


def _attach_a2a_payload(task: dict[str, Any]) -> dict[str, Any]:
    payload = build_a2a_payload_from_task(task)
    task["a2a_payload"] = payload
    task["instruction"] = payload["instruction"]
    return payload


def _mark_task_failed(task: dict[str, Any] | None) -> None:
    if task is not None:
        task["status"] = "failed"


def _failure_result(agent_label: str, exc: Exception) -> str:
    return f"{agent_label} task failed: {exc}"


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
        fields = sorted({*task.get("args", {}).keys(), *missing_fields})
        if missing_fields:
            summary = "Planner selected a workflow requiring additional fields."
        else:
            summary = "Planner selected an executable workflow; values omitted from memory."
        evidence.append(
            ExecutionEvidence(
                kind="planner_decision",
                agent="planner",
                operation=str(task.get("intent", "unknown")),
                status="interrupted" if missing_fields else "completed",
                fields=fields,
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
        operation=str(task.get("intent", "unknown")),
        status="started",
        fields=sorted(str(key) for key in task.get("args", {})),
        summary="Dispatched domain workflow; supplied values omitted from memory.",
    )


def _agent_result_evidence(
    agent: str,
    operation: str,
    *,
    completed: bool,
) -> ExecutionEvidence:
    return ExecutionEvidence(
        kind="agent_result",
        agent=agent,
        operation=operation,
        status="completed" if completed else "failed",
        summary=(
            "Domain workflow completed; returned values omitted from memory."
            if completed
            else "Domain workflow failed; failure details omitted from memory."
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
