import re
from typing import Literal

from pydantic import BaseModel

from multi_agent_system.common.mcp_tool_agent import MCPToolAgent
from multi_agent_system.a2a_servers.music_agent.schemas import MusicAgentResponse


MusicIntent = Literal[
    "albums_by_artist",
    "tracks_by_artist",
    "songs_by_genre",
    "check_song",
]


KNOWN_GENRES = (
    "rock",
    "jazz",
    "metal",
    "blues",
    "latin",
    "reggae",
    "pop",
    "classical",
    "alternative",
    "punk",
    "hip hop",
    "electronic",
    "world",
    "soundtrack",
    "opera",
)


class MusicRequest(BaseModel):
    intent: MusicIntent
    artist: str | None = None
    genre: str | None = None
    song_title: str | None = None


class MusicAgent(MCPToolAgent):
    async def ainvoke(self, query: str) -> MusicAgentResponse:
        request = self._parse_request(query)

        if error := self._validate_request(request):
            return error

        handlers = {
            "albums_by_artist": self._get_albums_by_artist,
            "tracks_by_artist": self._get_tracks_by_artist,
            "songs_by_genre": self._get_songs_by_genre,
            "check_song": self._check_song,
        }

        return await handlers[request.intent](request)

    def _parse_request(self, query: str) -> MusicRequest:
        normalized = query.lower()

        if self._is_album_query(normalized):
            return MusicRequest(
                intent="albums_by_artist",
                artist=self._extract_after_keywords(
                    query,
                    ["artist", "by", "from"],
                ),
            )

        # Important: check song existence before genre.
        # Example: "Let There Be Rock" contains "rock",
        # but it is a song title, not a genre query.
        if self._is_song_check_query(normalized):
            return MusicRequest(
                intent="check_song",
                song_title=self._extract_song_title(query),
            )

        if self._is_genre_query(normalized):
            return MusicRequest(
                intent="songs_by_genre",
                genre=self._extract_genre(query),
            )

        return MusicRequest(
            intent="tracks_by_artist",
            artist=self._extract_after_keywords(
                query,
                ["artist", "by", "from"],
            ),
        )

    def _extract_genre(self, text: str) -> str | None:
        normalized = text.lower()

        for genre in KNOWN_GENRES:
            if re.search(rf"\b{re.escape(genre)}\b", normalized):
                return genre

        value = self._extract_after_keywords(
            text,
            ["genre", "songs", "tracks", "music", "recommend"],
        )

        if value:
            return self._clean_extracted_value(value)

        return None

    def _validate_request(
        self,
        request: MusicRequest,
    ) -> MusicAgentResponse | None:
        if request.intent in {"albums_by_artist", "tracks_by_artist"}:
            if not request.artist:
                return MusicAgentResponse(
                    success=False,
                    content="Missing required field: artist.",
                )

        if request.intent == "songs_by_genre" and not request.genre:
            return MusicAgentResponse(
                success=False,
                content="Missing required field: genre.",
            )

        if request.intent == "check_song" and not request.song_title:
            return MusicAgentResponse(
                success=False,
                content="Missing required field: song_title.",
            )

        return None

    async def _get_albums_by_artist(
        self,
        request: MusicRequest,
    ) -> MusicAgentResponse:
        data = await self.call_tool(
            "get_albums_by_artist",
            {"artist": request.artist},
        )

        return MusicAgentResponse(
            success=True,
            content=f"Found albums for artist={request.artist}.",
            data=data,
        )

    async def _get_tracks_by_artist(
        self,
        request: MusicRequest,
    ) -> MusicAgentResponse:
        data = await self.call_tool(
            "get_tracks_by_artist",
            {"artist": request.artist},
        )

        return MusicAgentResponse(
            success=True,
            content=f"Found tracks for artist={request.artist}.",
            data=data,
        )

    async def _get_songs_by_genre(
        self,
        request: MusicRequest,
    ) -> MusicAgentResponse:
        data = await self.call_tool(
            "get_songs_by_genre",
            {"genre": request.genre},
        )

        return MusicAgentResponse(
            success=True,
            content=f"Found songs for genre={request.genre}.",
            data=data,
        )

    async def _check_song(
        self,
        request: MusicRequest,
    ) -> MusicAgentResponse:
        data = await self.call_tool(
            "check_for_songs",
            {"song_title": request.song_title},
        )

        if not data:
            return MusicAgentResponse(
                success=True,
                content=f"No song found matching title={request.song_title}.",
                data=[],
            )

        return MusicAgentResponse(
            success=True,
            content=f"Found song results for title={request.song_title}.",
            data=data,
        )

    def _is_album_query(self, text: str) -> bool:
        return "album" in text or "albums" in text

    def _is_genre_query(self, text: str) -> bool:
        return "genre" in text or any(
            re.search(rf"\b{re.escape(genre)}\b", text)
            for genre in KNOWN_GENRES
        )

    def _is_song_check_query(self, text: str) -> bool:
        return (
            "check" in text
            or "exists" in text
            or "do you have" in text
            or "song called" in text
            or "track called" in text
            or "song name" in text
            or "song title" in text
            or "check for song" in text
        )

    def _extract_after_keywords(
        self,
        text: str,
        keywords: list[str],
    ) -> str | None:
        normalized = text.strip()

        for keyword in keywords:
            pattern = rf"\b{re.escape(keyword)}\b\s+(.+)$"
            match = re.search(pattern, normalized, flags=re.IGNORECASE)

            if match:
                value = match.group(1).strip(" ?.\"'")
                return self._clean_extracted_value(value)

        return self._fallback_extract_value(normalized)

    def _extract_song_title(self, text: str) -> str | None:
        patterns = [
            r"check\s+for\s+song\s+(?:the\s+)?song\s+name\s+is\s+['\"]?(.+?)['\"]?$",
            r"check\s+for\s+song\s+(?:the\s+)?song\s+title\s+is\s+['\"]?(.+?)['\"]?$",
            r"check\s+for\s+song\s+['\"]?(.+?)['\"]?$",
            r"(?:song_title|song title)\s*(?:=|:|is)\s*['\"]?(.+?)['\"]?$",
            r"(?:song name|title)\s*(?:=|:|is)\s*['\"]?(.+?)['\"]?$",
            r"the\s+song\s+name\s+is\s+['\"]?(.+?)['\"]?$",
            r"check\s+if\s+the\s+song\s+['\"]?(.+?)['\"]?\s+exists",
            r"check\s+if\s+song\s+['\"]?(.+?)['\"]?\s+exists",
            r"check\s+song\s+['\"]?(.+?)['\"]?$",
            r"song\s+called\s+['\"]?(.+?)['\"]?$",
            r"track\s+called\s+['\"]?(.+?)['\"]?$",
            r"do you have\s+['\"]?(.+?)['\"]?$",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)

            if match:
                return match.group(1).strip(" ?.\"'")

        return None

    def _fallback_extract_value(self, text: str) -> str | None:
        cleaned = self._clean_extracted_value(text)
        return cleaned or None

    def _clean_extracted_value(self, value: str) -> str:
        stop_phrases = [
            "songs by",
            "tracks by",
            "albums by",
            "artist",
            "genre",
            "recommend",
            "retrieve",
            "list",
            "a list of",
            "provide",
            "show me",
            "find",
            "get",
            "music",
            "songs",
            "song",
            "tracks",
            "track",
            "albums",
            "album",
            "some",
            "a few",
            "please",
            "of",
        ]

        cleaned = value.strip(" ?.\"'")

        for phrase in stop_phrases:
            cleaned = re.sub(
                rf"\b{re.escape(phrase)}\b",
                "",
                cleaned,
                flags=re.IGNORECASE,
            )

        return re.sub(r"\s+", " ", cleaned).strip(" ?.\"'")
