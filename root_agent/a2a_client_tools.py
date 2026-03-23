import httpx
from langchain_core.tools import tool
from a2a.client import A2AClient

INVOICE_AGENT_URL = "http://localhost:8010"
MUSIC_AGENT_URL   = "http://localhost:8011"


async def _call_a2a_agent(base_url: str, query: str) -> str:
    """Send a query to an A2A agent and return its text response."""
    async with httpx.AsyncClient(timeout=60) as http_client:
        client = A2AClient(httpx_client=http_client, url=base_url)
        
        # Build the A2A message request
        from a2a.types import MessageSendParams, Message, TextPart, Role
        response = await client.send_message(
            MessageSendParams(
                message=Message(
                    role=Role.user,
                    parts=[TextPart(text=query)],
                )
            )
        )
        # Extract text from the response parts
        parts = response.result.status.message.parts if response.result else []
        return " ".join(p.text for p in parts if hasattr(p, "text"))


@tool
async def get_invoice_agent(request: str) -> str:
    """
    Consult this tool for any questions regarding customer invoices, unit prices, or
    assigned support employees.

    Args:
        request: The user's natural language question about invoices.
    """
    return await _call_a2a_agent(INVOICE_AGENT_URL, request)


@tool
async def get_music_agent(request: str) -> str:
    """
    Consult this tool for any questions about songs, albums, artists, or music genres.

    Args:
        request: The user's natural language question about music.
    """
    return await _call_a2a_agent(MUSIC_AGENT_URL, request)