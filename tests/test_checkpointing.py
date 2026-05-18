from pathlib import Path
from typing import Any

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from multi_agent_system.planner_app.checkpointing import build_checkpointer


def test_build_memory_checkpointer(monkeypatch: pytest.MonkeyPatch) -> None:
    from multi_agent_system import config

    monkeypatch.setattr(config.settings, "checkpoint_backend", "memory")

    checkpointer = build_checkpointer()

    assert isinstance(checkpointer, InMemorySaver)


def test_build_memory_checkpointer_is_case_insensitive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from multi_agent_system import config

    monkeypatch.setattr(config.settings, "checkpoint_backend", "MEMORY")

    checkpointer = build_checkpointer()

    assert isinstance(checkpointer, InMemorySaver)


def test_unsupported_checkpoint_backend_raises_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from multi_agent_system import config

    monkeypatch.setattr(config.settings, "checkpoint_backend", "redis")

    with pytest.raises(ValueError, match="Unsupported checkpoint backend"):
        build_checkpointer()


def test_sqlite_checkpointer_creates_parent_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pytest.importorskip("langgraph.checkpoint.sqlite")

    from multi_agent_system import config

    checkpoint_path = tmp_path / "nested" / "checkpoints.sqlite"

    monkeypatch.setattr(config.settings, "checkpoint_backend", "sqlite")
    monkeypatch.setattr(
        config.settings,
        "checkpoint_sqlite_path",
        str(checkpoint_path),
    )

    checkpointer: Any = build_checkpointer()

    assert checkpoint_path.parent.exists()
    assert checkpointer is not None

    close = getattr(checkpointer, "close", None)
    if callable(close):
        close()


def test_sqlite_checkpointer_can_be_used_as_context_manager(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pytest.importorskip("langgraph.checkpoint.sqlite")

    from multi_agent_system import config

    checkpoint_path = tmp_path / "checkpoints.sqlite"

    monkeypatch.setattr(config.settings, "checkpoint_backend", "sqlite")
    monkeypatch.setattr(
        config.settings,
        "checkpoint_sqlite_path",
        str(checkpoint_path),
    )

    checkpointer = build_checkpointer()

    assert checkpointer is not None

    close = getattr(checkpointer, "close", None)
    if callable(close):
        close()