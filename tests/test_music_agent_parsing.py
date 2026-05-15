import pytest

from multi_agent_system.a2a_servers.music_agent.agent import MusicAgent


@pytest.mark.parametrize(
    ("query", "expected_intent", "expected_artist"),
    [
        ("Find tracks by artist AC/DC", "tracks_by_artist", "AC/DC"),
        ("Find tracks by AC/DC", "tracks_by_artist", "AC/DC"),
        ("Find albums by artist Accept", "albums_by_artist", "Accept"),
        ("Find albums by Accept", "albums_by_artist", "Accept"),
    ],
)
def test_music_agent_parses_artist_requests(
    query: str,
    expected_intent: str,
    expected_artist: str,
) -> None:
    agent = MusicAgent()

    request = agent._parse_request(query)

    assert request.intent == expected_intent
    assert request.artist == expected_artist


@pytest.mark.parametrize(
    ("query", "expected_genre"),
    [
        ("Recommend songs by genre rock", "Rock"),
        ("Recommend some rock tracks", "Rock"),
        ("Retrieve a list of jazz tracks", "Jazz"),
        ("Find some heavy metal music", "Heavy Metal"),
        ("Recommend genre Bossa Nova", "Bossa Nova"),
    ],
)
def test_music_agent_parses_genre_requests(
    query: str,
    expected_genre: str,
) -> None:
    agent = MusicAgent()

    request = agent._parse_request(query)

    assert request.intent == "songs_by_genre"
    assert request.genre == expected_genre


@pytest.mark.parametrize(
    ("query", "expected_title"),
    [
        ("Check for song Ligia", "Ligia"),
        ("Check song Rolling in the Deep", "Rolling in the Deep"),
        ("Check for song Let There Be Rock", "Let There Be Rock"),
        ("song_title=Desafinado", "Desafinado"),
        ("Do you have Garota De Ipanema", "Garota De Ipanema"),
    ],
)
def test_music_agent_parses_song_check_requests(
    query: str,
    expected_title: str,
) -> None:
    agent = MusicAgent()

    request = agent._parse_request(query)

    assert request.intent == "check_song"
    assert request.song_title == expected_title


def test_song_title_with_genre_word_does_not_become_genre_request() -> None:
    agent = MusicAgent()

    request = agent._parse_request("Check for song Let There Be Rock")

    assert request.intent == "check_song"
    assert request.song_title == "Let There Be Rock"
    assert request.genre is None


def test_music_agent_missing_artist_fails_validation() -> None:
    agent = MusicAgent()

    request = agent._parse_request("Find tracks by")
    error = agent._validate_request(request)

    assert error is not None
    assert error.success is False
    assert error.content == "Missing required field: artist."
