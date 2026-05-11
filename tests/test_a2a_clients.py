import asyncio

from multi_agent_system.a2a_client.invoice_client import InvoiceA2AClient
from multi_agent_system.a2a_client.music_client import MusicA2AClient


async def main() -> None:
    invoice_client = InvoiceA2AClient()
    music_client = MusicA2AClient()

    invoice_result = await invoice_client.get_latest_invoice("5")
    print("Invoice result:")
    print(invoice_result)

    music_result = await music_client.get_tracks_by_artist("AC/DC")
    print("\nMusic result:")
    print(music_result)


if __name__ == "__main__":
    asyncio.run(main())