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

    if intent == "invoice_query":
        return _build_invoice_query_instruction(args)

    if intent == "music_query":
        return _build_music_query_instruction(args)

    if intent == "latest_invoice":
        customer_id = _require_arg(args, "customer_id", intent)
        return f"Get latest invoice for customer_id={customer_id}"

    if intent == "invoice_detail":
        invoice_id = _require_arg(args, "invoice_id", intent)
        return f"Get invoice detail for invoice_id={invoice_id}"

    if intent == "invoice_summary":
        customer_id = _require_arg(args, "customer_id", intent)
        return f"Get invoice summary for customer_id={customer_id}"

    if intent == "customer_support_employee":
        customer_id = _require_arg(args, "customer_id", intent)
        return f"Get support employee for customer_id={customer_id}"

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


def _build_invoice_query_instruction(args: dict[str, Any]) -> str:
    if _has_arg(args, "invoice_id"):
        invoice_id = _require_arg(args, "invoice_id", "invoice_query")
        return f"Get invoice detail for invoice_id={invoice_id} with support employee"

    customer_id = _require_arg(args, "customer_id", "invoice_query")
    limit = _optional_arg(args, "limit")
    sort_by = _optional_arg(args, "sort_by")
    sort_order = _optional_arg(args, "sort_order")

    parts = ["Get"]
    if limit:
        parts.append(limit)
    if sort_by == "invoice_date" and sort_order == "desc":
        parts.append("most recent")
    elif sort_by == "unit_price":
        parts.append("invoices sorted by unit price")
        if sort_order:
            parts.append(sort_order)
        return " ".join(parts) + f" for customer_id={customer_id} with support employee"
    else:
        parts.append("invoices")

    if "invoices" not in parts[-1]:
        parts.append("invoices")

    return " ".join(parts) + f" for customer_id={customer_id} with support employee"


def _build_music_query_instruction(args: dict[str, Any]) -> str:
    search_type = _require_arg(args, "search_type", "music_query")

    if search_type == "artist":
        artist = _require_arg(args, "artist", "music_query")
        return f"Find tracks by artist {artist}"

    if search_type == "albums_by_artist":
        artist = _require_arg(args, "artist", "music_query")
        return f"Find albums by artist {artist}"

    if search_type == "genre":
        genre = _require_arg(args, "genre", "music_query")
        return f"Recommend songs by genre {genre}"

    if search_type == "song_title":
        song_title = _require_arg(args, "song_title", "music_query")
        return f"Check for song {song_title}"

    raise TaskInstructionError(
        "music_query args.search_type must be one of: "
        "artist, albums_by_artist, genre, song_title."
    )


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


def _optional_arg(args: dict[str, Any], key: str) -> str | None:
    value = args.get(key)
    if value is None:
        return None

    text = str(value).strip()
    return text or None


def _has_arg(args: dict[str, Any], key: str) -> bool:
    return _optional_arg(args, key) is not None
