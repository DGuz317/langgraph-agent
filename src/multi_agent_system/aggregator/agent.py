import json
from typing import Any

from multi_agent_system.aggregator.schemas import (
    AggregatorInput,
    AggregatorOutput,
)


class AggregatorAgent:
    def invoke(self, data: AggregatorInput) -> AggregatorOutput:
        if not data.results:
            return AggregatorOutput(
                final_answer="No agent results were returned."
            )

        sections: list[str] = []

        for result in data.results:
            sections.append(
                self._format_result(
                    agent=result.agent,
                    raw_result=result.result,
                )
            )

        return AggregatorOutput(
            final_answer="\n\n".join(sections)
        )

    def _format_result(self, agent: str, raw_result: Any) -> str:
        title = f"{self._format_agent_name(agent)} result"
        parsed = self._parse_result(raw_result)

        if isinstance(parsed, dict):
            return self._format_dict_result(title, parsed)

        if isinstance(parsed, list):
            return self._format_list_result(title, parsed)

        return f"{title}:\n{parsed}"

    def _parse_result(self, raw_result: Any) -> Any:
        if isinstance(raw_result, str):
            try:
                return json.loads(raw_result)
            except json.JSONDecodeError:
                return raw_result

        return raw_result

    def _format_dict_result(self, title: str, data: dict[str, Any]) -> str:
        success = data.get("success")
        content = data.get("content")
        payload = data.get("data")

        if success is False:
            return f"{title}:\nFailed: {content}"

        if payload is None:
            return f"{title}:\n{content}"

        formatted_payload = json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )

        return f"{title}:\n{content}\n\nData:\n{formatted_payload}"

    def _format_list_result(self, title: str, data: list[Any]) -> str:
        if not data:
            return f"{title}:\nNo records found."

        formatted_payload = json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )

        return f"{title}:\nData:\n{formatted_payload}"

    def _format_agent_name(self, agent: str) -> str:
        return agent.replace("_", " ").title()