from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel

from multi_agent_system.config import settings
from multi_agent_system.common.observability import configure_observability


def get_llm() -> BaseChatModel:
    configure_observability()
    provider, model = _model_provider_and_name()
    kwargs = _provider_kwargs(provider)
    return init_chat_model(
        model,
        model_provider=provider,
        temperature=settings.llm_temperature,
        **kwargs,
    )


def _model_provider_and_name() -> tuple[str, str]:
    if ":" in settings.llm_model:
        provider, model = settings.llm_model.split(":", 1)
        return _normalize_provider(provider), model

    return _normalize_provider(settings.model_provider), settings.llm_model


def _normalize_provider(provider: str) -> str:
    if provider == "google":
        return "google_genai"
    return provider


def _provider_kwargs(provider: str) -> dict[str, str]:
    if provider == "ollama":
        return {"base_url": settings.ollama_api_url}

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for openai models.")
        return {"api_key": settings.openai_api_key}

    if provider == "google_genai":
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required for google_genai models.")
        return {"google_api_key": settings.google_api_key}

    if provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for anthropic models.")
        return {"api_key": settings.anthropic_api_key}

    return {}
