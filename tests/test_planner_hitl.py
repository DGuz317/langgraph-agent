from multi_agent_system.planner_app.hitl import (
    ask_for_missing_info,
    ensure_required_task_fields,
    extract_missing_fields,
)


def test_ask_for_missing_song_title() -> None:
    question = ask_for_missing_info(["song_title"])

    assert question == "Which song title should I check?"


def test_ask_for_missing_artist() -> None:
    question = ask_for_missing_info(["artist"])

    assert question == "Which artist should I search for?"


def test_ask_for_missing_genre() -> None:
    question = ask_for_missing_info(["genre"])

    assert question == "Which genre should I search for?"


def test_ask_for_missing_music_search_type() -> None:
    question = ask_for_missing_info(["music_search_type"])

    assert "artist" in question
    assert "genre" in question


def test_ask_for_missing_invoice_id() -> None:
    question = ask_for_missing_info(["invoice_id"])

    assert question == "Could you provide the invoice ID?"


def test_extract_song_title_from_plain_answer() -> None:
    result = extract_missing_fields(
        user_response="Ligia",
        missing_fields=["song_title"],
    )

    assert result == {"song_title": "Ligia"}


def test_extract_artist_from_plain_answer() -> None:
    result = extract_missing_fields(
        user_response="AC/DC",
        missing_fields=["artist"],
    )

    assert result == {"artist": "AC/DC"}


def test_extract_genre_from_plain_answer() -> None:
    result = extract_missing_fields(
        user_response="rock",
        missing_fields=["genre"],
    )

    assert result == {"genre": "rock"}


def test_extract_music_search_type_artist() -> None:
    result = extract_missing_fields(
        user_response="artist: AC/DC",
        missing_fields=["music_search_type"],
    )

    assert result == {
        "music_search_type": "artist",
        "artist": "AC/DC",
    }


def test_extract_music_search_type_genre() -> None:
    result = extract_missing_fields(
        user_response="genre: rock",
        missing_fields=["music_search_type"],
    )

    assert result == {
        "music_search_type": "genre",
        "genre": "rock",
    }


def test_music_search_type_plain_answer_does_not_guess() -> None:
    result = extract_missing_fields(
        user_response="AC/DC",
        missing_fields=["music_search_type"],
    )

    assert result == {}


def test_extract_customer_id_from_plain_number() -> None:
    result = extract_missing_fields(
        user_response="5",
        missing_fields=["customer_id"],
    )

    assert result == {"customer_id": "5"}


def test_extract_customer_id_from_sentence() -> None:
    result = extract_missing_fields(
        user_response="my customer id is 5",
        missing_fields=["customer_id"],
    )

    assert result == {"customer_id": "5"}


def test_extract_invoice_id_from_plain_number() -> None:
    result = extract_missing_fields(
        user_response="361",
        missing_fields=["invoice_id"],
    )

    assert result == {"invoice_id": "361"}


def test_extract_invoice_id_from_sentence() -> None:
    result = extract_missing_fields(
        user_response="invoice id is 361",
        missing_fields=["invoice_id"],
    )

    assert result == {"invoice_id": "361"}


def test_required_field_guard_adds_missing_customer_id() -> None:
    result = ensure_required_task_fields(
        {
            "tasks": [
                {
                    "agent": "invoice",
                    "instruction": "Show the latest invoice.",
                    "missing_fields": [],
                }
            ]
        }
    )

    assert result["missing_fields"] == ["customer_id"]
    assert result["tasks"][0]["missing_fields"] == ["customer_id"]


def test_required_field_guard_accepts_existing_customer_id() -> None:
    result = ensure_required_task_fields(
        {
            "tasks": [
                {
                    "agent": "invoice",
                    "instruction": "Show the latest invoice for customer_id=5.",
                    "missing_fields": ["customer_id"],
                }
            ]
        }
    )

    assert result["missing_fields"] == []
    assert result["tasks"][0]["missing_fields"] == []


def test_required_field_guard_adds_missing_invoice_id() -> None:
    result = ensure_required_task_fields(
        {
            "tasks": [
                {
                    "agent": "invoice",
                    "instruction": "Get invoice detail.",
                    "missing_fields": [],
                }
            ]
        }
    )

    assert result["missing_fields"] == ["invoice_id"]


def test_required_field_guard_adds_music_search_type_for_vague_search() -> None:
    result = ensure_required_task_fields(
        {
            "tasks": [
                {
                    "agent": "music",
                    "instruction": "Recommend some songs.",
                    "missing_fields": [],
                }
            ]
        }
    )

    assert result["missing_fields"] == ["music_search_type"]


def test_required_field_guard_accepts_music_genre_descriptor() -> None:
    result = ensure_required_task_fields(
        {
            "tasks": [
                {
                    "agent": "music",
                    "instruction": "Recommend 5 Jazz songs.",
                    "missing_fields": [],
                }
            ]
        }
    )

    assert result["missing_fields"] == []


def test_required_field_guard_adds_missing_artist_value() -> None:
    result = ensure_required_task_fields(
        {
            "tasks": [
                {
                    "agent": "music",
                    "instruction": "Find tracks by artist.",
                    "missing_fields": [],
                }
            ]
        }
    )

    assert result["missing_fields"] == ["artist"]


def test_extract_music_search_type_genre_without_colon() -> None:
    result = extract_missing_fields(
        user_response="genre rock",
        missing_fields=["music_search_type"],
    )

    assert result == {
        "music_search_type": "genre",
        "genre": "rock",
    }


def test_extract_music_search_type_artist_without_colon() -> None:
    result = extract_missing_fields(
        user_response="artist AC/DC",
        missing_fields=["music_search_type"],
    )

    assert result == {
        "music_search_type": "artist",
        "artist": "AC/DC",
    }
