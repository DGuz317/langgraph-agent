from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ModelProvider = Literal["ollama", "openai", "google", "anthropic"]

class Settings(BaseSettings):
    # LLM
    model_provider: ModelProvider = "ollama"
    llm_model: str = "gpt-oss"
    llm_temperature: float = 0.0

    # Ollama
    ollama_api_url: str = "http://localhost:11434"

    # OpenAI
    openai_api_key: str | None = None

    # Google Gemini
    google_api_key: str | None = None

    # Anthropic
    anthropic_api_key: str | None = None

    # Database
    sqlite_db: str

    # MCP
    mcp_server_url: str = "http://localhost:10000/mcp"

    # A2A
    invoice_a2a_url: str = "http://localhost:11001"
    music_a2a_url: str = "http://localhost:11002"
    a2a_timeout_seconds: int = 30

    # LangSmith
    langsmith_api_key: str | None = None
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_tracing: bool = True
    langsmith_project: str = "multi-agent-system"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()