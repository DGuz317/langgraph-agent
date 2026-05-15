import re
from typing import Any

from langgraph.types import interrupt


def ask_for_missing_info(missing_fields: list[str]) -> str:
    if "customer_id" in missing_fields:
        return "Could you provide your customer ID?"

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


def _extract_labeled_value(text: str, labels: list[str]) -> str | None:
    for label in labels:
        pattern = rf"\b{re.escape(label)}\s*(?:=|:|is)?\s*(.+)$"
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            return match.group(1).strip(" ?.\"'")

    return None
