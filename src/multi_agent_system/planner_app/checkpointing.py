"""Checkpointer factory for the planner LangGraph app."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from langgraph.checkpoint.memory import InMemorySaver

from multi_agent_system.config import settings


def build_memory_checkpointer() -> InMemorySaver:
    """Build an in-memory checkpointer for tests and simple local runs."""
    return InMemorySaver()


@asynccontextmanager
async def build_async_checkpointer_context() -> AsyncIterator[Any]:
    """Build the configured checkpointer.

    Supported backends:
    - memory: volatile in-process checkpointing.
    - sqlite: persistent async SQLite checkpointing.

    SQLite uses an async context manager because LangGraph's
    AsyncSqliteSaver.from_conn_string(...) returns a context manager.
    """
    backend = settings.checkpoint_backend.strip().lower()

    if backend == "memory":
        yield InMemorySaver()
        return

    if backend == "sqlite":
        try:
            from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        except ImportError as exc:
            raise RuntimeError(
                "SQLite checkpoint backend requires "
                "`langgraph-checkpoint-sqlite` and `aiosqlite`.\n\n"
                "Install with:\n"
                "uv add langgraph-checkpoint-sqlite aiosqlite"
            ) from exc

        db_path = Path(settings.checkpoint_sqlite_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        async with AsyncSqliteSaver.from_conn_string(str(db_path)) as saver:
            yield saver

        return

    raise ValueError(
        "Unsupported checkpoint backend: "
        f"{settings.checkpoint_backend!r}. "
        "Expected one of: memory, sqlite."
    )