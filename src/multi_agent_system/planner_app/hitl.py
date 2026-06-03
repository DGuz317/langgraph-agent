import re
from typing import Any

from langgraph.types import interrupt


CRITICAL_MISSING_FIELDS = {
    "customer_id",
    "invoice_id",
    "music_search_type",
    "artist",
    "genre",
    "song_title",
}


def ask_for_missing_info(missing_fields: list[str]) -> str:
    if "customer_id" in missing_fields:
        return "Could you provide your customer ID?"

    if "invoice_id" in missing_fields:
        return "Could you provide the invoice ID?"

    if "music_search_type" in missing_fields:
        return (
            "Do you want to search by artist or by genre? "
        )


    if "artist" in missing_fields:
        return "Which artist should I search for?"

    if "genre" in missing_fields:
        return "Which genre should I search for?"

    if "song_title" in missing_fields:
        return "Which song title should I check?"

    return "Could you provide the missing information?"


def extract_missing_fields(
    user_response: str,
    missing_fields: list[str],
) -> dict[str, Any]:
    extracted: dict[str, Any] = {}
    cleaned = user_response.strip(" ?.\"'")

    if "customer_id" in missing_fields:
        match = re.search(
            r"\b(?:customer_id|customer id|id)\s*(?:=|:|is)?\s*(\d+)",
            user_response,
            flags=re.IGNORECASE,
        )

        if match:
            extracted["customer_id"] = match.group(1)
        elif cleaned.isdigit():
            extracted["customer_id"] = cleaned

    if "invoice_id" in missing_fields:
        match = re.search(
            r"\b(?:invoice_id|invoice id|id)\s*(?:=|:|is)?\s*(\d+)",
            user_response,
            flags=re.IGNORECASE,
        )

        if match:
            extracted["invoice_id"] = match.group(1)
        elif cleaned.isdigit():
            extracted["invoice_id"] = cleaned

    if "music_search_type" in missing_fields:
        artist = _extract_labeled_value(user_response, ["artist", "by artist"])
        genre = _extract_labeled_value(user_response, ["genre", "by genre"])

        if artist:
            extracted["music_search_type"] = "artist"
            extracted["artist"] = artist

        if genre:
            extracted["music_search_type"] = "genre"
            extracted["genre"] = genre

    if "artist" in missing_fields:
        extracted["artist"] = cleaned

    if "genre" in missing_fields:
        extracted["genre"] = cleaned

    if "song_title" in missing_fields:
        extracted["song_title"] = cleaned

    return {key: value for key, value in extracted.items() if value}


def ensure_required_task_fields(planner_output: dict[str, Any]) -> dict[str, Any]:
    """Return planner output with deterministic critical missing fields annotated."""
    updated = dict(planner_output)
    tasks: list[dict[str, Any]] = []

    for raw_task in updated.get("tasks", []):
        if not isinstance(raw_task, dict):
            continue

        task = dict(raw_task)
        agent = str(task.get("agent") or "")
        instruction = str(task.get("instruction") or "")
        detected = set(_detect_missing_fields(agent, instruction))
        existing = {
            str(field).strip()
            for field in task.get("missing_fields", [])
            if str(field).strip()
        }
        unresolved_existing = {
            field
            for field in existing & CRITICAL_MISSING_FIELDS
            if not _field_is_present(field, instruction)
        }
        task_missing = sorted(
            (existing - CRITICAL_MISSING_FIELDS) | unresolved_existing | detected
        )
        task["missing_fields"] = task_missing
        tasks.append(task)

    updated["tasks"] = tasks
    updated["missing_fields"] = sorted(
        {
            str(field).strip()
            for task in tasks
            for field in task.get("missing_fields", [])
            if str(field).strip()
        }
    )
    return updated


def interrupt_for_missing_info(missing_fields: list[str]) -> dict[str, Any]:
    question = ask_for_missing_info(missing_fields)

    user_response = interrupt(
        {
            "type": "missing_required_fields",
            "question": question,
            "missing_fields": missing_fields,
        }
    )

    return extract_missing_fields(
        user_response=str(user_response).strip(),
        missing_fields=missing_fields,
    )


def _detect_missing_fields(agent: str, instruction: str) -> list[str]:
    if agent == "invoice":
        return _detect_missing_invoice_fields(instruction)

    if agent == "music":
        return _detect_missing_music_fields(instruction)

    return []


def _detect_missing_invoice_fields(instruction: str) -> list[str]:
    missing: list[str] = []

    if _needs_customer_id(instruction) and not _field_is_present(
        "customer_id",
        instruction,
    ):
        missing.append("customer_id")

    if _needs_invoice_id(instruction) and not _field_is_present(
        "invoice_id",
        instruction,
    ):
        missing.append("invoice_id")

    return missing


def _detect_missing_music_fields(instruction: str) -> list[str]:
    missing: list[str] = []

    if _needs_artist(instruction) and not _field_is_present("artist", instruction):
        missing.append("artist")

    if _needs_genre(instruction) and not _field_is_present("genre", instruction):
        missing.append("genre")

    if _needs_song_title(instruction) and not _field_is_present(
        "song_title",
        instruction,
    ):
        missing.append("song_title")

    if (
        _needs_music_search_type(instruction)
        and not any(field in missing for field in ("artist", "genre", "song_title"))
        and not _field_is_present("music_search_type", instruction)
        and not _field_is_present("artist", instruction)
        and not _field_is_present("genre", instruction)
    ):
        missing.append("music_search_type")

    return missing


def _needs_customer_id(instruction: str) -> bool:
    text = instruction.lower()
    customer_scoped = (
        "latest invoice",
        "recent invoice",
        "invoice summary",
        "total invoice spending",
        "total spending",
        "spending",
        "sorted by unit price",
        "support employee",
        "support rep",
    )
    return any(phrase in text for phrase in customer_scoped) or (
        "customer" in text and any(term in text for term in ("invoice", "billing"))
    )


def _needs_invoice_id(instruction: str) -> bool:
    text = instruction.lower()
    invoice_scoped = (
        "invoice detail",
        "invoice details",
        "invoice by id",
    )
    return any(phrase in text for phrase in invoice_scoped) or (
        re.search(r"\binvoice[_ ]id\b", text) is not None
    )


def _needs_artist(instruction: str) -> bool:
    text = instruction.lower()
    return (
        "by artist" in text
        or re.search(r"\bartist\s*(?:=|:|is)?\s*$", text) is not None
    )


def _needs_genre(instruction: str) -> bool:
    text = instruction.lower()
    return (
        "by genre" in text
        or re.search(r"\bgenre\s*(?:=|:|is)?\s*$", text) is not None
    )


def _needs_song_title(instruction: str) -> bool:
    text = instruction.lower()
    return (
        any(term in text for term in ("check", "exists", "exist", "find"))
        and "song" in text
        and not _field_is_present("song_title", instruction)
        and re.search(
            r"\bsong\s*(?:=|:|is|named|called|title)?\s*$",
            text,
        )
        is not None
    )


def _needs_music_search_type(instruction: str) -> bool:
    text = instruction.lower()
    if not any(term in text for term in ("recommend", "search", "find", "list")):
        return False

    if not any(term in text for term in ("song", "songs", "track", "tracks")):
        return False

    if _has_music_descriptor(instruction):
        return False

    return True


def _has_music_descriptor(instruction: str) -> bool:
    if (
        _field_is_present("artist", instruction)
        or _field_is_present("genre", instruction)
        or _field_is_present("music_search_type", instruction)
    ):
        return True

    match = re.search(
        r"\b(?:recommend|search|find|list)\b(?P<detail>.*?)\b(?:songs?|tracks?)\b",
        instruction,
        flags=re.IGNORECASE,
    )
    if not match:
        return False

    detail = re.sub(r"\b\d+\b", " ", match.group("detail"))
    words = [
        word.lower()
        for word in re.findall(r"[A-Za-z][\w/-]*", detail)
        if word.lower() not in {"some", "a", "an", "few", "several", "me", "for"}
    ]
    return bool(words)


def _field_is_present(field: str, instruction: str) -> bool:
    if field == "customer_id":
        return _has_labeled_number(instruction, ["customer_id", "customer id"])

    if field == "invoice_id":
        return _has_labeled_number(instruction, ["invoice_id", "invoice id"])

    if field == "music_search_type":
        return (
            _has_labeled_value(instruction, ["music_search_type", "music search type"])
            or _has_labeled_value(instruction, ["by artist"])
            or _has_labeled_value(instruction, ["by genre"])
        )

    if field == "artist":
        return _has_labeled_value(instruction, ["artist", "by artist"])

    if field == "genre":
        return _has_labeled_value(instruction, ["genre", "by genre"])

    if field == "song_title":
        return _has_labeled_value(instruction, ["song_title", "song title", "song"])

    return False


def _has_labeled_number(text: str, labels: list[str]) -> bool:
    return any(
        re.search(
            rf"\b{re.escape(label)}\s*(?:=|:|is)?\s*\d+\b",
            text,
            flags=re.IGNORECASE,
        )
        for label in labels
    )


def _has_labeled_value(text: str, labels: list[str]) -> bool:
    return any(_extract_labeled_value(text, [label]) for label in labels)


def _extract_labeled_value(text: str, labels: list[str]) -> str | None:
    for label in labels:
        pattern = rf"\b{re.escape(label)}\s*(?:=|:|is)?\s*(.+)$"
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            return match.group(1).strip(" ?.\"'")

    return None
