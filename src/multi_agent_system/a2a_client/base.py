import json
from typing import Any
from uuid import uuid4

import httpx


class A2AClientError(RuntimeError):
    pass


class BaseA2AClient:
    def __init__(self, url: str, timeout_seconds: int = 30) -> None:
        self.url = url
        self.timeout_seconds = timeout_seconds

    async def send_message(self, text: str) -> dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid4()),
            "method": "SendMessage",
            "params": {
                "message": {
                    "role": "ROLE_USER",
                    "parts": [
                        {
                            "text": text,
                        }
                    ],
                    "messageId": str(uuid4()),
                }
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
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
        body = response.json()

        if "error" in body:
            raise A2AClientError(json.dumps(body["error"], indent=2))

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