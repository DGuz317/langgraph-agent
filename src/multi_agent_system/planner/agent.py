import re
from uuid import uuid4

from multi_agent_system.planner.schemas import PlannedTask, PlannerOutput


class PlannerAgent:
    def invoke(self, user_input: str) -> PlannerOutput:
        text = user_input.lower()

        tasks: list[PlannedTask] = []

        if self._is_invoice_request(text):
            tasks.append(
                PlannedTask(
                    id=str(uuid4()),
                    agent="invoice",
                    instruction=self._build_invoice_instruction(user_input),
                    required_fields=self._missing_invoice_fields(user_input),
                )
            )

        if self._is_music_request(text):
            tasks.append(
                PlannedTask(
                    id=str(uuid4()),
                    agent="music",
                    instruction=self._build_music_instruction(user_input),
                    required_fields=self._missing_music_fields(user_input),
                )
            )

        if not tasks:
            return PlannerOutput(
                answer=[],
                confidence=0.0,
                requires_aggregation=False,
                missing_fields=[],
            )

        missing_fields = sorted(
            {
                field
                for task in tasks
                for field in task.required_fields
            }
        )

        return PlannerOutput(
            answer=tasks,
            confidence=0.9,
            requires_aggregation=len(tasks) > 1,
            missing_fields=missing_fields,
        )

    def _is_invoice_request(self, text: str) -> bool:
        keywords = ["invoice", "billing", "unit price", "customer id", "customer_id"]
        return any(keyword in text for keyword in keywords)

    def _is_music_request(self, text: str) -> bool:
        keywords = [
            "music",
            "song",
            "songs",
            "track",
            "tracks",
            "album",
            "albums",
            "artist",
            "genre",
            "rock",
            "jazz",
            "metal",
            "ac/dc",
            "queen",
        ]
        return any(keyword in text for keyword in keywords)

    def _missing_invoice_fields(self, user_input: str) -> list[str]:
        text = user_input.lower()

        if "invoice" not in text and "unit price" not in text:
            return []

        if self._extract_number(user_input, ["customer_id", "customer id", "id"]):
            return []

        return ["customer_id"]

    def _missing_music_fields(self, user_input: str) -> list[str]:
        text = user_input.lower()

        if "check" in text or "exists" in text or "do you have" in text:
            return []

        if "genre" in text or "rock" in text or "jazz" in text or "metal" in text:
            return []

        if "artist" in text or "by " in text or "ac/dc" in text or "queen" in text:
            return []

        if "song" in text or "track" in text or "album" in text:
            return ["artist"]

        return []

    def _build_invoice_instruction(self, user_input: str) -> str:
        customer_id = self._extract_number(
            user_input,
            ["customer_id", "customer id", "id"],
        )

        if customer_id:
            return f"Get latest invoice for customer_id={customer_id}"

        return "Get latest invoice for the customer"

    def _build_music_instruction(self, user_input: str) -> str:
        return user_input

    def _extract_number(self, text: str, field_names: list[str]) -> str | None:
        normalized = text.lower()

        for field_name in field_names:
            pattern = rf"{re.escape(field_name)}\s*(?:=|:|is)?\s*(\d+)"
            match = re.search(pattern, normalized)

            if match:
                return match.group(1)

        return None

    def _extract_song_title(self, text: str) -> str | None:
        patterns = [
            r"check\s+for\s+song\s+(.+)$",
            r"check\s+song\s+(.+)$",
            r"song\s+called\s+(.+)$",
            r"track\s+called\s+(.+)$",
            r"song\s+(.+?)\s+exists",
            r"track\s+(.+?)\s+exists",
            r"do you have\s+(.+)$",
            r"check\s+(.+)$",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)

            if match:
                return match.group(1).strip(" ?.\"'")

        return None
    
    def _is_song_check_query(self, text: str) -> bool:
        return (
            "check" in text
            or "exists" in text
            or "do you have" in text
            or "song called" in text
            or "track called" in text
            or "check for song" in text
        )