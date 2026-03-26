import asyncio
from uuid import uuid4
from a2a.client import ClientFactory
from a2a.types import Message, Part, TextPart, Role

async def main():
    client = await ClientFactory.connect('http://localhost:8010')
    request_message = Message(
        role=Role.user,
        messageId=uuid4().hex, 
        parts=[
            Part(root=TextPart(text='My customer id is 1. What is my most recent invoice?'))
        ]
    )
    print("Sending request to Invoice Agent...")
    async for event in client.send_message(request_message):
        print(event)

if __name__ == "__main__":
    asyncio.run(main())