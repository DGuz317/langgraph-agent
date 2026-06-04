from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any

from multi_agent_system.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def configure_observability() -> None:
    """Configure LangSmith before LangChain/LangGraph objects are used."""
    enabled = settings.langsmith_tracing and bool(settings.langsmith_api_key)
    os.environ["LANGSMITH_TRACING"] = "true" if enabled else "false"
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint

    if settings.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key

    try:
        from langsmith.run_trees import configure

        configure(
            enabled=enabled,
            project_name=settings.langsmith_project,
            metadata=_base_metadata(),
            tags=["multi-agent-system", settings.model_provider],
        )
    except Exception:
        logger.debug("Unable to configure LangSmith programmatically.", exc_info=True)

    logger.info(
        "LangSmith tracing %s for project %s.",
        "enabled" if enabled else "disabled",
        settings.langsmith_project,
    )


def trace_config(
    *,
    run_name: str,
    thread_id: str | None = None,
    request_id: str | None = None,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    merged_metadata = {
        **_base_metadata(),
        **({"thread_id": thread_id} if thread_id else {}),
        **({"request_id": request_id} if request_id else {}),
        **(metadata or {}),
    }
    return {
        "run_name": run_name,
        "tags": ["multi-agent-system", *(tags or [])],
        "metadata": merged_metadata,
    }


def _base_metadata() -> dict[str, Any]:
    return {
        "model_provider": settings.model_provider,
        "llm_model": settings.llm_model,
    }
