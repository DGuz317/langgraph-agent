import json
from typing import Any
from uuid import uuid4

import httpx

from multi_agent_system.common.errors import A2AClientError


class BaseA2AClient:
    def __init__(self, url: str, timeout_seconds: int = 30, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.url = url
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    async def send_message(
        self,
        text: str,
        *,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        parts: list[dict[str, Any]] = [{"text": text}]

        if data is not None:
            parts.insert(0, {"data": data})

        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid4()),
            "method": "SendMessage",
            "params": {
                "message": {
                    "role": "ROLE_USER",
                    "parts": parts,
                    "messageId": str(uuid4()),
                }
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, transport=self.transport) as client:
                response = await client.post(
                    self.url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "A2A-Version": "1.0",
                    },
                )

            response.raise_for_status()

            try:
                body = response.json()
            except ValueError as exc:
                raise A2AClientError("A2A response was not valid JSON.") from exc

        except httpx.TimeoutException as exc:
            raise A2AClientError(
                f"A2A request timed out after {self.timeout_seconds} seconds."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise A2AClientError(
                f"A2A service returned HTTP {exc.response.status_code}: {exc.response.text}"
            ) from exc

        except httpx.HTTPError as exc:
            raise A2AClientError(f"A2A request failed: {exc}") from exc

        if "error" in body:
            raise A2AClientError(
                f"A2A JSON-RPC error: {json.dumps(body['error'], ensure_ascii=False)}"
            )

        return body

    async def ask(self, text: str) -> str:
        body = await self.send_message(text)
        return self._extract_text_response(body)

    async def ask_payload(self, payload: dict[str, Any]) -> str:
        """Send structured task data while retaining text compatibility."""
        instruction = payload.get("instruction")

        if not isinstance(instruction, str) or not instruction.strip():
            raise A2AClientError("Structured A2A payload requires instruction text.")

        body = await self.send_message(instruction, data=payload)
        return self._extract_text_response(body)

    def _extract_text_response(self, body: dict[str, Any]) -> str:
        result = body.get("result")

        if not isinstance(result, dict):
            raise A2AClientError("A2A response missing result object.")

        parts = self._extract_parts(result)

        text_parts: list[str] = []

        for part in parts:
            if not isinstance(part, dict):
                continue

            text = part.get("text")

            if text is None:
                continue

            if not isinstance(text, str):
                raise A2AClientError("A2A response text content must be a string.")

            cleaned = text.strip()

            if cleaned:
                text_parts.append(cleaned)

        if not text_parts:
            has_text_key = any(
                isinstance(part, dict) and "text" in part
                for part in parts
            )

            if has_text_key:
                raise A2AClientError("A2A response contained empty text response.")

            raise A2AClientError("A2A response missing text content.")

        return "\n".join(text_parts)

    def _extract_parts(self, result: dict[str, Any]) -> list[Any]:
        # Shape 1:
        # {"result": {"message": {"parts": [{"text": "..."}]}}}
        message = result.get("message")

        if isinstance(message, dict):
            parts = message.get("parts")

            if isinstance(parts, list):
                return parts

        # Shape 2:
        # {"result": {"parts": [{"text": "..."}]}}
        direct_parts = result.get("parts")

        if isinstance(direct_parts, list):
            return direct_parts

        raise A2AClientError("A2A response missing message parts.")
