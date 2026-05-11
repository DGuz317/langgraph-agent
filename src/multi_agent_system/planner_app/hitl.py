import re
from typing import Any

from langgraph.types import interrupt


def ask_for_missing_info(missing_fields: list[str]) -> str:
    if "customer_id" in missing_fields:
        return "Could you provide your customer ID?"

    if "artist" in missing_fields:
        return "Which artist should I search for?"

    if "genre" in missing_fields:
        return "Which genre should I search for?"

    return "Could you provide the missing information?"


def extract_missing_fields(user_response: str, missing_fields: list[str]) -> dict[str, Any]:
    extracted: dict[str, Any] = {}

    if "customer_id" in missing_fields:
        match = re.search(r"\b(?:customer_id|customer id|id)\s*(?:=|:|is)?\s*(\d+)", user_response.lower())
        if match:
            extracted["customer_id"] = match.group(1)

    if "artist" in missing_fields:
        cleaned = user_response.strip(" ?.\"'")
        extracted["artist"] = cleaned

    if "genre" in missing_fields:
        cleaned = user_response.strip(" ?.\"'")
        extracted["genre"] = cleaned

    return extracted


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
        user_response=str(user_response),
        missing_fields=missing_fields,
    )