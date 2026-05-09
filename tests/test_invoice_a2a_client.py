import asyncio
import json
from uuid import uuid4

import httpx


INVOICE_A2A_URL = "http://localhost:11001/a2a/jsonrpc/"


async def main() -> None:
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid4()),
        "method": "SendMessage",
        "params": {
            "message": {
                "role": "ROLE_USER",
                "parts": [
                    {
                        "text": "Get latest invoice for customer_id=5"
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

    print("Status:", response.status_code)
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())