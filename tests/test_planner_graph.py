from multi_agent_system.planner_app import nodes


def test_build_hitl_planner_input_appends_collected_details() -> None:
    result = nodes._build_hitl_planner_input(
        "show albums",
        {"artist": "Queen"},
    )

    assert result == (
        "show albums\n\n"
        "Additional information collected from the user: artist=Queen"
    )


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
