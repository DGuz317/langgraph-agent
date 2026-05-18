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

    async def send_message(self, text: str) -> dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid4()),
            "method": "SendMessage",
            "params": {
                "message": {
                    "role": "ROLE_USER",
                    "parts": [{"text": text}],
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

    def extract_text(self, response: dict[str, Any]) -> str:
        result = response.get("result", {})

        # Common message-only result shape.
        parts = result.get("parts", [])
        for part in parts:
            if "text" in part:
                return part["text"]

        # Some SDK responses wrap message under "message".
        message = result.get("message", {})
        parts = message.get("parts", [])
        for part in parts:
            if "text" in part:
                return part["text"]

        return json.dumps(response, indent=2)

    async def ask(self, text: str) -> str:
        response = await self.send_message(text)
        return self.extract_text(response)