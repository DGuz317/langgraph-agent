import re
from typing import Any

from langgraph.types import interrupt


def _extract_number(text: str, field_names: list[str]) -> str | None:
    for field_name in field_names:
        pattern = rf"\b{re.escape(field_name)}\s*(?:=|:|is)?\s*(\d+)"
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            return match.group(1)

    return None


def ask_for_missing_info(missing_fields: list[str]) -> str:
    if "customer_id" in missing_fields:
        return "Could you provide your customer ID?"

    if "invoice_id" in missing_fields:
        return "Which invoice ID should I use?"

    if "artist" in missing_fields:
        return "Which artist should I search for?"

    if "genre" in missing_fields:
        return "Which genre should I search for?"

    if "song_title" in missing_fields:
        return "Which song title should I check?"

    return "Could you provide the missing information?"


def extract_missing_fields(user_response: str, missing_fields: list[str]) -> dict[str, Any]:
    extracted: dict[str, Any] = {}

    if "customer_id" in missing_fields:
        customer_id = _extract_number(user_response, ["customer_id", "customer id", "id"])

        if customer_id:
            extracted["customer_id"] = customer_id
        elif len(missing_fields) == 1 and user_response.strip().isdigit():
            extracted["customer_id"] = user_response.strip()

    if "invoice_id" in missing_fields:
        invoice_id = _extract_number(user_response, ["invoice_id", "invoice id", "invoice"])

        if invoice_id:
            extracted["invoice_id"] = invoice_id
        elif len(missing_fields) == 1 and user_response.strip().isdigit():
            extracted["invoice_id"] = user_response.strip()

    if "artist" in missing_fields:
        cleaned = user_response.strip(" ?.\"'")
        extracted["artist"] = cleaned

    if "genre" in missing_fields:
        cleaned = user_response.strip(" ?.\"'")
        extracted["genre"] = cleaned

    if "song_title" in missing_fields:
        cleaned = user_response.strip(" ?.\"'")
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
