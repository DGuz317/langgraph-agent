from multi_agent_system.planner_app import nodes


def test_missing_info_node_rebuilds_song_title_instruction(monkeypatch) -> None:
    def fake_interrupt_for_missing_info(missing_fields: list[str]) -> dict:
        assert missing_fields == ["song_title"]
        return {"song_title": "Ligia"}

    monkeypatch.setattr(
        nodes,
        "interrupt_for_missing_info",
        fake_interrupt_for_missing_info,
    )

    state = {
        "user_input": "check for song",
        "missing_fields": ["song_title"],
        "planner_output": {
            "tasks": [
                {
                    "agent": "music",
                    "instruction": "Check for song",
                    "missing_fields": ["song_title"],
                }
            ]
        },
    }

    result = nodes.missing_info_node(state)
    task = result["planner_output"]["tasks"][0]

    assert task["instruction"] == "Check for song Ligia"
    assert task["missing_fields"] == []
    assert result["missing_fields"] == []
    assert result["song_title"] == "Ligia"


def test_missing_info_node_rebuilds_customer_id_instruction(monkeypatch) -> None:
    def fake_interrupt_for_missing_info(missing_fields: list[str]) -> dict:
        assert missing_fields == ["customer_id"]
        return {"customer_id": "5"}

    monkeypatch.setattr(
        nodes,
        "interrupt_for_missing_info",
        fake_interrupt_for_missing_info,
    )

    state = {
        "user_input": "what is my latest invoice",
        "missing_fields": ["customer_id"],
        "planner_output": {
            "tasks": [
                {
                    "agent": "invoice",
                    "instruction": "Get latest invoice",
                    "missing_fields": ["customer_id"],
                }
            ]
        },
    }

    result = nodes.missing_info_node(state)
    task = result["planner_output"]["tasks"][0]

    assert task["instruction"] == "Get latest invoice for customer_id=5"
    assert task["missing_fields"] == []
    assert result["missing_fields"] == []
    assert result["customer_id"] == "5"


def test_missing_info_node_preserves_invoice_unit_price_intent(monkeypatch) -> None:
    def fake_interrupt_for_missing_info(missing_fields: list[str]) -> dict:
        assert missing_fields == ["customer_id"]
        return {"customer_id": "5"}

    monkeypatch.setattr(
        nodes,
        "interrupt_for_missing_info",
        fake_interrupt_for_missing_info,
    )

    state = {
        "user_input": "show my invoices sorted by unit price",
        "missing_fields": ["customer_id"],
        "planner_output": {
            "tasks": [
                {
                    "agent": "invoice",
                    "intent": "invoices_by_unit_price",
                    "instruction": "Get invoices sorted by unit price",
                    "missing_fields": ["customer_id"],
                }
            ]
        },
    }

    result = nodes.missing_info_node(state)
    task = result["planner_output"]["tasks"][0]

    assert task["instruction"] == "Get invoices sorted by unit price for customer_id=5"
    assert task["missing_fields"] == []
    assert result["missing_fields"] == []
    assert result["customer_id"] == "5"


def test_missing_info_node_rebuilds_music_artist_from_music_search_type(monkeypatch) -> None:
    def fake_interrupt_for_missing_info(missing_fields: list[str]) -> dict:
        assert missing_fields == ["music_search_type"]
        return {
            "music_search_type": "artist",
            "artist": "AC/DC",
        }

    monkeypatch.setattr(
        nodes,
        "interrupt_for_missing_info",
        fake_interrupt_for_missing_info,
    )

    state = {
        "user_input": "recommend some songs",
        "missing_fields": ["music_search_type"],
        "planner_output": {
            "tasks": [
                {
                    "agent": "music",
                    "intent": "clarify_music_search",
                    "instruction": "Ask whether the user wants music by artist or by genre.",
                    "missing_fields": ["music_search_type"],
                }
            ]
        },
    }

    result = nodes.missing_info_node(state)
    task = result["planner_output"]["tasks"][0]

    assert task["instruction"] == "Find tracks by artist AC/DC"
    assert task["missing_fields"] == []
    assert result["missing_fields"] == []
    assert result["music_search_type"] == "artist"
    assert result["artist"] == "AC/DC"


def test_missing_info_node_rebuilds_music_genre_from_music_search_type(monkeypatch) -> None:
    def fake_interrupt_for_missing_info(missing_fields: list[str]) -> dict:
        assert missing_fields == ["music_search_type"]
        return {
            "music_search_type": "genre",
            "genre": "rock",
        }

    monkeypatch.setattr(
        nodes,
        "interrupt_for_missing_info",
        fake_interrupt_for_missing_info,
    )

    state = {
        "user_input": "recommend some songs",
        "missing_fields": ["music_search_type"],
        "planner_output": {
            "tasks": [
                {
                    "agent": "music",
                    "intent": "clarify_music_search",
                    "instruction": "Ask whether the user wants music by artist or by genre.",
                    "missing_fields": ["music_search_type"],
                }
            ]
        },
    }

    result = nodes.missing_info_node(state)
    task = result["planner_output"]["tasks"][0]

    assert task["instruction"] == "Recommend songs by genre rock"
    assert task["missing_fields"] == []
    assert result["missing_fields"] == []
    assert result["music_search_type"] == "genre"
    assert result["genre"] == "rock"


def test_route_after_missing_info_goes_to_music() -> None:
    from multi_agent_system.planner_app.edges import route_after_planner

    state = {
        "missing_fields": [],
        "planner_output": {
            "tasks": [
                {
                    "agent": "music",
                    "instruction": "Check for song Ligia",
                    "missing_fields": [],
                }
            ]
        },
    }

    assert route_after_planner(state) == "music"
