import pytest

from multi_agent_system.planner_app.task_instructions import (
    TaskInstructionError,
    build_instruction_from_task,
)


def test_build_latest_invoice_instruction() -> None:
    task = {
        "intent": "latest_invoice",
        "args": {"customer_id": "5"},
    }

    assert build_instruction_from_task(task) == "Get latest invoice for customer_id=5"


def test_build_invoices_by_unit_price_instruction() -> None:
    task = {
        "intent": "invoices_by_unit_price",
        "args": {"customer_id": "5"},
    }

    assert (
        build_instruction_from_task(task)
        == "Get invoices sorted by unit price for customer_id=5"
    )


def test_build_tracks_by_artist_instruction() -> None:
    task = {
        "intent": "tracks_by_artist",
        "args": {"artist": "AC/DC"},
    }

    assert build_instruction_from_task(task) == "Find tracks by artist AC/DC"


def test_build_albums_by_artist_instruction() -> None:
    task = {
        "intent": "albums_by_artist",
        "args": {"artist": "AC/DC"},
    }

    assert build_instruction_from_task(task) == "Find albums by artist AC/DC"


def test_build_songs_by_genre_instruction() -> None:
    task = {
        "intent": "songs_by_genre",
        "args": {"genre": "rock"},
    }

    assert build_instruction_from_task(task) == "Recommend songs by genre rock"


def test_build_check_song_instruction() -> None:
    task = {
        "intent": "check_song",
        "args": {"song_title": "Ligia"},
    }

    assert build_instruction_from_task(task) == "Check for song Ligia"


def test_clarify_music_search_is_not_executable() -> None:
    task = {
        "intent": "clarify_music_search",
        "args": {},
    }

    with pytest.raises(TaskInstructionError):
        build_instruction_from_task(task)


def test_missing_required_arg_raises_error() -> None:
    task = {
        "intent": "songs_by_genre",
        "args": {},
    }

    with pytest.raises(TaskInstructionError):
        build_instruction_from_task(task)