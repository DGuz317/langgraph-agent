from pathlib import Path

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from multi_agent_system.planner_app.checkpointing import (
    build_async_checkpointer_context,
    build_memory_checkpointer,
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_build_memory_checkpointer() -> None:
    checkpointer = build_memory_checkpointer()

    assert isinstance(checkpointer, InMemorySaver)


@pytest.mark.anyio
async def test_async_checkpointer_context_uses_memory_backend(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from multi_agent_system import config

    monkeypatch.setattr(config.settings, "checkpoint_backend", "memory")

    async with build_async_checkpointer_context() as checkpointer:
        assert isinstance(checkpointer, InMemorySaver)


@pytest.mark.anyio
async def test_async_checkpointer_context_is_case_insensitive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from multi_agent_system import config

    monkeypatch.setattr(config.settings, "checkpoint_backend", "MEMORY")

    async with build_async_checkpointer_context() as checkpointer:
        assert isinstance(checkpointer, InMemorySaver)


@pytest.mark.anyio
async def test_unsupported_checkpoint_backend_raises_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from multi_agent_system import config

    monkeypatch.setattr(config.settings, "checkpoint_backend", "redis")

    with pytest.raises(ValueError, match="Unsupported checkpoint backend"):
        async with build_async_checkpointer_context():
            pass


@pytest.mark.anyio
async def test_sqlite_checkpointer_creates_parent_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pytest.importorskip("langgraph.checkpoint.sqlite.aio")

    from multi_agent_system import config

    checkpoint_path = tmp_path / "nested" / "checkpoints.sqlite"

    monkeypatch.setattr(config.settings, "checkpoint_backend", "sqlite")
    monkeypatch.setattr(
        config.settings,
        "checkpoint_sqlite_path",
        str(checkpoint_path),
    )

    async with build_async_checkpointer_context() as checkpointer:
        assert checkpoint_path.parent.exists()
        assert checkpointer is not None


@pytest.mark.anyio
async def test_sqlite_checkpointer_context_can_be_opened(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pytest.importorskip("langgraph.checkpoint.sqlite.aio")

    from multi_agent_system import config

    checkpoint_path = tmp_path / "checkpoints.sqlite"

    monkeypatch.setattr(config.settings, "checkpoint_backend", "sqlite")
    monkeypatch.setattr(
        config.settings,
        "checkpoint_sqlite_path",
        str(checkpoint_path),
    )

    async with build_async_checkpointer_context() as checkpointer:
        assert checkpointer is not None