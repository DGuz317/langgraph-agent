import asyncio
import httpx
from uuid import uuid4
from a2a.client import ClientFactory, ClientConfig
from a2a.types import (
    Message, 
    Part, 
    TextPart, 
    Role,
)
 
BASE_URL = 'http://localhost:8040'
 
async def send_message(text: str):
    print(f"\n{'='*60}")
    print(f"Query: {text}")
    print('='*60)

    # 1. Create a custom HTTP client with an extended timeout (e.g., 120 seconds)
    custom_http_client = httpx.AsyncClient(timeout=300.0)
    
    # 2. Inject it into the ClientConfig
    config = ClientConfig(httpx_client=custom_http_client)

    # 3. Connect using the CORRECT parameter name: 'client_config'
    client = await ClientFactory.connect(BASE_URL, client_config=config)

    request_message = Message(
        role=Role.user,
        messageId=uuid4().hex, 
        parts=[
            Part(root=TextPart(text=text))
        ]
    )

    async for event in client.send_message(request_message):
        print(event)
 
async def main():
    # Test 1: Invoice only
    await send_message('My customer id is 1. What is my most recent invoice?')
 
    # Test 2: Music only
    await send_message('Show me tracks by Aerosmith')
 
    # Test 3: Both agents
    await send_message('Show me AC/DC tracks and my latest invoice. My customer id is 2.')
 
if __name__ == "__main__":
    asyncio.run(main())