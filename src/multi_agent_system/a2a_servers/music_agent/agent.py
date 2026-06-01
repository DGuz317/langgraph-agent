from multi_agent_system.a2a_servers.music_agent.prompts import MUSIC_AGENT_SYSTEM_PROMPT
from multi_agent_system.a2a_servers.music_agent.schemas import MusicAgentResponse
from multi_agent_system.common.agent_runtime import (
    AgentRuntime,
    LangChainAgentRuntime,
)


MUSIC_TOOL_NAMES = {
    "get_albums_by_artist",
    "get_tracks_by_artist",
    "get_songs_by_genre",
    "check_for_songs",
    "query_music_database",
}


class MusicAgent:
    def __init__(self, runtime: AgentRuntime | None = None) -> None:
        self._runtime = runtime or LangChainAgentRuntime(
            agent_name="music",
            system_prompt=MUSIC_AGENT_SYSTEM_PROMPT,
            allowed_tools=MUSIC_TOOL_NAMES,
        )

    async def ainvoke(self, query: str) -> MusicAgentResponse:
        try:
            result = await self._runtime.ainvoke(query)
        except Exception as exc:
            return MusicAgentResponse(
                success=False,
                content=f"Music agent failed: {exc}",
            )

        return MusicAgentResponse(
            success=result.success,
            content=result.content,
        )
