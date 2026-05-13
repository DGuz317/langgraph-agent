import json
import os
from uuid import uuid4

import httpx
import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_A2A_INTEGRATION_TESTS") != "1",
    reason="Set RUN_A2A_INTEGRATION_TESTS=1 and start the invoice A2A service to run this test.",
)

INVOICE_A2A_URL = "http://localhost:11001/a2a/jsonrpc/"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_invoice_a2a_jsonrpc_get_latest_invoice() -> None:
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid4()),
        "method": "SendMessage",
        "params": {
            "message": {
                "role": "ROLE_USER",
                "parts": [
                    {
                        "text": "Get latest invoice for customer_id=5",
                    }
                ],
                "messageId": str(uuid4()),
            }
        },
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            INVOICE_A2A_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "A2A-Version": "1.0",
            },
        )

    body = response.json()

    assert response.status_code == 200
    assert body.get("jsonrpc") == "2.0"
    assert "error" not in body, json.dumps(body, indent=2)
    assert "result" in body
