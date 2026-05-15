import json

from multi_agent_system.aggregator.agent import AggregatorAgent
from multi_agent_system.aggregator.schemas import (
    AgentResult,
    AggregatorInput,
)


def aggregate(
    results: list[AgentResult],
    user_input: str = "test user input",
) -> str:
    data = AggregatorInput(
        user_input=user_input,
        results=results,
    )

    return AggregatorAgent().invoke(data).final_answer


def test_aggregator_returns_empty_message_when_no_results() -> None:
    final_answer = aggregate([])

    assert final_answer == "No agent results were returned."


def test_aggregator_formats_structured_success_result_with_data() -> None:
    final_answer = aggregate(
        [
            AgentResult(
                agent="music_agent",
                result=json.dumps(
                    {
                        "success": True,
                        "content": "Found songs for genre=Rock.",
                        "data": [
                            {
                                "SongName": "For Those About To Rock",
                                "ArtistName": "AC/DC",
                            }
                        ],
                    }
                ),
            )
        ]
    )

    assert "Music Agent result:" in final_answer
    assert "Found songs for genre=Rock." in final_answer
    assert "Data:" in final_answer
    assert "For Those About To Rock" in final_answer
    assert "AC/DC" in final_answer


def test_aggregator_formats_structured_failure_result() -> None:
    final_answer = aggregate(
        [
            AgentResult(
                agent="invoice_agent",
                result=json.dumps(
                    {
                        "success": False,
                        "content": "Missing customer_id.",
                        "data": None,
                    }
                ),
            )
        ]
    )

    assert final_answer == "Invoice Agent result:\nFailed: Missing customer_id."


def test_aggregator_formats_dict_result_without_data() -> None:
    final_answer = aggregate(
        [
            AgentResult(
                agent="invoice_agent",
                result={
                    "success": True,
                    "content": "No invoice found for customer_id=999999.",
                },
            )
        ]
    )

    assert final_answer == (
        "Invoice Agent result:\n"
        "No invoice found for customer_id=999999."
    )


def test_aggregator_formats_plain_text_result() -> None:
    final_answer = aggregate(
        [
            AgentResult(
                agent="music_agent",
                result="Music service is unavailable.",
            )
        ]
    )

    assert final_answer == "Music Agent result:\nMusic service is unavailable."


def test_aggregator_formats_invalid_json_as_plain_text() -> None:
    final_answer = aggregate(
        [
            AgentResult(
                agent="music_agent",
                result="{invalid json",
            )
        ]
    )

    assert final_answer == "Music Agent result:\n{invalid json"


def test_aggregator_formats_list_result() -> None:
    final_answer = aggregate(
        [
            AgentResult(
                agent="music_agent",
                result=[
                    {
                        "SongName": "Restless and Wild",
                        "ArtistName": "Accept",
                    }
                ],
            )
        ]
    )

    assert "Music Agent result:" in final_answer
    assert "Data:" in final_answer
    assert "Restless and Wild" in final_answer


def test_aggregator_formats_empty_list_result() -> None:
    final_answer = aggregate(
        [
            AgentResult(
                agent="music_agent",
                result=[],
            )
        ]
    )

    assert final_answer == "Music Agent result:\nNo records found."


def test_aggregator_combines_multiple_agent_results_in_order() -> None:
    final_answer = aggregate(
        [
            AgentResult(
                agent="invoice_agent",
                result=json.dumps(
                    {
                        "success": True,
                        "content": "Found latest invoice.",
                        "data": {"InvoiceId": 77, "CustomerId": 5},
                    }
                ),
            ),
            AgentResult(
                agent="music_agent",
                result=json.dumps(
                    {
                        "success": True,
                        "content": "Found songs for genre=Jazz.",
                        "data": [{"SongName": "Desafinado", "ArtistName": "Antônio Carlos Jobim"}],
                    },
                    ensure_ascii=False,
                ),
            ),
        ]
    )

    invoice_index = final_answer.index("Invoice Agent result:")
    music_index = final_answer.index("Music Agent result:")

    assert invoice_index < music_index
    assert "Found latest invoice." in final_answer
    assert "Found songs for genre=Jazz." in final_answer
    assert "Antônio Carlos Jobim" in final_answer
