import json
from pathlib import Path

from google.protobuf.json_format import ParseDict
from a2a.types import AgentCard


AGENT_CARDS_DIR = Path(__file__).resolve().parents[1] / "agent_cards"


def load_agent_card(file_name: str) -> AgentCard:
    card_path = AGENT_CARDS_DIR / file_name

    if not card_path.exists():
        raise FileNotFoundError(f"Agent card not found: {card_path}")

    with card_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return ParseDict(data, AgentCard())