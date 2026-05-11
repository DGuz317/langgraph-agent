from pydantic import BaseModel


class MusicAgentResponse(BaseModel):
    success: bool
    content: str
    data: list[dict] | dict | None = None