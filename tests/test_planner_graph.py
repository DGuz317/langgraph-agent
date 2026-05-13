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