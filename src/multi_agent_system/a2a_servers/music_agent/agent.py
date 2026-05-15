import re
from typing import Literal

from pydantic import BaseModel

from multi_agent_system.a2a_servers.music_agent.schemas import MusicAgentResponse
from multi_agent_system.common.mcp_tool_agent import MCPToolAgent


MusicIntent = Literal[
    "albums_by_artist",
    "tracks_by_artist",
    "songs_by_genre",
    "check_song",
]


# Keep the longest / most specific genre names before shorter overlapping names.
KNOWN_GENRES = (
    "Alternative & Punk",
    "Electronica/Dance",
    "Hip Hop/Rap",
    "Easy Listening",
    "Heavy Metal",
    "Rock And Roll",
    "Bossa Nova",
    "Science Fiction",
    "Soundtrack",
    "Classical",
    "Alternative",
    "TV Shows",
    "Reggae",
    "Comedy",
    "Metal",
    "Blues",
    "Latin",
    "Opera",
    "World",
    "Drama",
    "Jazz",
    "Rock",
    "Pop",
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
        normalized = query.lower().strip()

        # Song lookup must be checked before genre routing.
        # Example: "Check for song Let There Be Rock" should not become genre=Rock.
        if self._is_song_check_query(normalized):
            return MusicRequest(
                intent="check_song",
                song_title=self._extract_song_title(query),
            )

        if self._is_album_query(normalized):
            return MusicRequest(
                intent="albums_by_artist",
                artist=self._extract_artist(query),
            )

        if self._is_explicit_artist_query(normalized):
            return MusicRequest(
                intent="tracks_by_artist",
                artist=self._extract_artist(query),
            )

        if self._is_genre_query(normalized):
            return MusicRequest(
                intent="songs_by_genre",
                genre=self._extract_genre(query),
            )

        return MusicRequest(
            intent="tracks_by_artist",
            artist=self._extract_artist(query),
        )

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
        return bool(re.search(r"\balbums?\b", text))

    def _is_explicit_artist_query(self, text: str) -> bool:
        return bool(
            re.search(r"\bartist\b", text)
            or re.search(r"\btracks?\s+by\b", text)
            or re.search(r"\bsongs?\s+by\b", text)
        ) and "genre" not in text

    def _is_genre_query(self, text: str) -> bool:
        if "genre" in text:
            return True

        recommendation_markers = (
            "recommend",
            "suggest",
            "find",
            "get",
            "retrieve",
            "list",
            "songs",
            "tracks",
            "music",
        )

        has_recommendation_marker = any(marker in text for marker in recommendation_markers)
        has_known_genre = self._find_known_genre(text) is not None

        return has_recommendation_marker and has_known_genre

    def _is_song_check_query(self, text: str) -> bool:
        return (
            bool(
                re.search(
                    r"\b(song_title|song title|song name|track_title|track title|title)"
                    r"\s*(?:=|:|is)\s*",
                    text,
                )
            )
            or "check" in text
            or "exists" in text
            or "do you have" in text
            or "song called" in text
            or "track called" in text
            or "song name" in text
            or "song title" in text
            or "check for song" in text
        )

    def _extract_artist(self, text: str) -> str | None:
        patterns = [
            r"\bartist\s*(?:=|:|is)?\s*(.+)$",
            r"\bby\s+artist\s+(.+)$",
            r"\btracks?\s+by\s+(.+)$",
            r"\bsongs?\s+by\s+(.+)$",
            r"\balbums?\s+by\s+(.+)$",
            r"\bby\s+(.+)$",
            r"\bfrom\s+(.+)$",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return self._clean_extracted_value(match.group(1))

        return self._clean_extracted_value(text) or None

    def _extract_genre(self, text: str) -> str | None:
        explicit_value = self._extract_explicit_genre_value(text)
        if explicit_value:
            known_genre = self._find_known_genre(explicit_value)
            return known_genre or self._clean_extracted_value(explicit_value)

        known_genre = self._find_known_genre(text)
        if known_genre:
            return known_genre

        fallback_value = self._clean_extracted_value(text)
        return fallback_value or None

    def _extract_explicit_genre_value(self, text: str) -> str | None:
        patterns = [
            r"\bgenre\s*(?:=|:|is)?\s*(.+)$",
            r"\bby\s+genre\s+(.+)$",
            r"\bsongs?\s+by\s+genre\s+(.+)$",
            r"\btracks?\s+by\s+genre\s+(.+)$",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip(" ?.\"'")

        return None

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

    def _find_known_genre(self, text: str) -> str | None:
        normalized = text.lower()

        for genre in KNOWN_GENRES:
            pattern = rf"(?<!\w){re.escape(genre.lower())}(?!\w)"
            if re.search(pattern, normalized):
                return genre

        return None

    def _clean_extracted_value(self, value: str) -> str:
        stop_phrases = [
            "songs by genre",
            "tracks by genre",
            "songs by",
            "tracks by",
            "albums by",
            "artist",
            "genre",
            "recommend",
            "suggest",
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
