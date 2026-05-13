import json
import os
from uuid import uuid4

import httpx
import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_A2A_INTEGRATION_TESTS") != "1",
    reason="Set RUN_A2A_INTEGRATION_TESTS=1 and start the music A2A service to run this test.",
)

MUSIC_A2A_URL = "http://localhost:11002/a2a/jsonrpc/"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_music_a2a_jsonrpc_find_tracks_by_artist() -> None:
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid4()),
        "method": "SendMessage",
        "params": {
            "message": {
                "role": "ROLE_USER",
                "parts": [
                    {
                        "text": "Find tracks by artist AC/DC",
                    }
                ],
                "messageId": str(uuid4()),
            }
        },
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            MUSIC_A2A_URL,
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
