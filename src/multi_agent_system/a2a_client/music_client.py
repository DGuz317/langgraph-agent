from multi_agent_system.a2a_client.base import BaseA2AClient
from multi_agent_system.config import settings


class MusicA2AClient(BaseA2AClient):
    def __init__(self) -> None:
        super().__init__(
            url=f"{settings.music_a2a_url.rstrip('/')}/a2a/jsonrpc/",
            timeout_seconds=settings.a2a_timeout_seconds,
        )

    async def get_tracks_by_artist(self, artist: str) -> str:
        return await self.ask(f"Find tracks by artist {artist}")

    async def get_albums_by_artist(self, artist: str) -> str:
        return await self.ask(f"Show albums by artist {artist}")

    async def get_songs_by_genre(self, genre: str) -> str:
        return await self.ask(f"Recommend {genre} songs")

    async def check_song(self, song_title: str) -> str:
        return await self.ask(f"Check if song called {song_title} exists")