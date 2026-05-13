from multi_agent_system.planner_app.hitl import (
    ask_for_missing_info,
    extract_missing_fields,
)


def test_ask_for_missing_song_title() -> None:
    question = ask_for_missing_info(["song_title"])

    assert question == "Which song title should I check?"


def test_extract_song_title_from_plain_answer() -> None:
    result = extract_missing_fields(
        user_response="Ligia",
        missing_fields=["song_title"],
    )

    assert result == {"song_title": "Ligia"}


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