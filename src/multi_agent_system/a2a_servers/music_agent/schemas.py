from typing import Literal

from pydantic import BaseModel, Field

from multi_agent_system.common.execution_evidence import ExecutionEvidence

# TODO: THis
MusicIntent = Literal[
    "music_query",
    "albums_by_artist",
    "tracks_by_artist",
    "songs_by_genre",
    "check_song",
]


class MusicRequest(BaseModel):
    intent: MusicIntent
    search_type: str | None = None
    artist: str | None = None
    genre: str | None = None
    song_title: str | None = None


class MusicTaskPayload(BaseModel):
    agent: Literal["music"]
    intent: MusicIntent
    args: dict[str, str] = Field(default_factory=dict)
    instruction: str | None = None

    def to_request(self) -> MusicRequest:
        return MusicRequest(
            intent=self.intent,
            search_type=self.args.get("search_type"),
            artist=self.args.get("artist"),
            genre=self.args.get("genre"),
            song_title=self.args.get("song_title"),
        )


class MusicAgentResponse(BaseModel):
    success: bool
    content: str
    data: list[dict] | dict | None = None
    execution_evidence: list[ExecutionEvidence] = Field(default_factory=list)
