from typing import Any


class TaskInstructionError(ValueError):
    """Raised when a planner task cannot be converted into an executable instruction."""


def build_a2a_payload_from_task(task: dict[str, Any]) -> dict[str, Any]:
    args = task.get("args") or {}

    if not isinstance(args, dict):
        raise TaskInstructionError("task args must be a dictionary.")

    return {
        "agent": _require_task_field(task, "agent"),
        "intent": _require_task_field(task, "intent"),
        "args": dict(args),
        "instruction": build_instruction_from_task(task),
    }


def build_instruction_from_task(task: dict[str, Any]) -> str:
    intent = task.get("intent")
    args = task.get("args") or {}

    if intent == "latest_invoice":
        customer_id = _require_arg(args, "customer_id", intent)
        return f"Get latest invoice for customer_id={customer_id}"

    if intent == "all_invoices":
        customer_id = _require_arg(args, "customer_id", intent)
        return f"Get all invoices for customer_id={customer_id}"

    if intent == "latest_invoice_support_employee":
        customer_id = _require_arg(args, "customer_id", intent)
        return f"Get support employee for latest invoice for customer_id={customer_id}"

    if intent == "invoices_by_unit_price":
        customer_id = _require_arg(args, "customer_id", intent)
        return f"Get invoices sorted by unit price for customer_id={customer_id}"

    if intent == "tracks_by_artist":
        artist = _require_arg(args, "artist", intent)
        return f"Find tracks by artist {artist}"

    if intent == "albums_by_artist":
        artist = _require_arg(args, "artist", intent)
        return f"Find albums by artist {artist}"

    if intent == "songs_by_genre":
        genre = _require_arg(args, "genre", intent)
        return f"Recommend songs by genre {genre}"

    if intent == "check_song":
        song_title = _require_arg(args, "song_title", intent)
        return f"Check for song {song_title}"

    if intent == "clarify_music_search":
        raise TaskInstructionError(
            "clarify_music_search is not executable. It must be resolved through HITL first."
        )

    raise TaskInstructionError(f"Unsupported task intent: {intent}")


def _require_task_field(task: dict[str, Any], key: str) -> str:
    value = task.get(key)

    if value is None:
        raise TaskInstructionError(f"Missing required task field '{key}'.")

    text = str(value).strip()

    if not text:
        raise TaskInstructionError(f"Required task field '{key}' is empty.")

    return text


def _require_arg(args: dict[str, Any], key: str, intent: str) -> str:
    value = args.get(key)

    if value is None:
        raise TaskInstructionError(
            f"Missing required arg '{key}' for intent '{intent}'."
        )

    text = str(value).strip()

    if not text:
        raise TaskInstructionError(
            f"Required arg '{key}' for intent '{intent}' is empty."
        )

    return text
