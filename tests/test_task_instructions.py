from multi_agent_system.planner_app.task_instructions import build_instruction_from_task


def test_build_latest_invoice_instruction() -> None:
    task = {
        "intent": "latest_invoice",
        "args": {"customer_id": "5"},
    }

    assert build_instruction_from_task(task) == "Get latest invoice for customer_id=5"


def test_build_invoice_unit_price_instruction() -> None:
    task = {
        "intent": "invoices_by_unit_price",
        "args": {"customer_id": "5"},
    }

    assert build_instruction_from_task(task) == (
        "Get invoices sorted by unit price for customer_id=5"
    )


def test_build_music_genre_instruction() -> None:
    task = {
        "intent": "songs_by_genre",
        "args": {"genre": "rock"},
    }

    assert build_instruction_from_task(task) == "Recommend songs by genre rock"


def test_build_music_artist_instruction() -> None:
    task = {
        "intent": "tracks_by_artist",
        "args": {"artist": "AC/DC"},
    }

    assert build_instruction_from_task(task) == "Find tracks by artist AC/DC"


def test_build_check_song_instruction() -> None:
    task = {
        "intent": "check_song",
        "args": {"song_title": "Ligia"},
    }

    assert build_instruction_from_task(task) == "Check for song Ligia"