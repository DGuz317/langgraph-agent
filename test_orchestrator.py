import asyncio
import httpx
from uuid import uuid4
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig
from a2a.types import (
    Message, 
    MessageSendParams, 
    Part, 
    TextPart, 
    Role,
    SendMessageRequest,
)
 
BASE_URL = 'http://localhost:8040'
 
async def send_message(text: str):
    print(f"\n{'='*60}")
    print(f"Query: {text}")
    print('='*60)

    client = await ClientFactory.connect(BASE_URL)

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
 
asyncio.run(main())