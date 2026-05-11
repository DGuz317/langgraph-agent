import json

from multi_agent_system.aggregator.schemas import (
    AgentResult,
    AggregatorInput,
    AggregatorOutput,
)


class AggregatorAgent:
    def invoke(self, data: AggregatorInput) -> AggregatorOutput:
        sections: list[str] = []

        for result in data.results:
            parsed = self._try_parse_json(result.result)

            if parsed:
                sections.append(
                    self._format_structured_result(
                        agent=result.agent,
                        data=parsed,
                    )
                )
            else:
                sections.append(
                    f"{result.agent.title()} result:\n{result.result}"
                )

        return AggregatorOutput(
            final_answer="\n\n".join(sections)
        )

    def _try_parse_json(self, text: str) -> dict | None:
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return None

        return parsed if isinstance(parsed, dict) else None

    def _format_structured_result(self, agent: str, data: dict) -> str:
        success = data.get("success")
        content = data.get("content")
        payload = data.get("data")

        title = f"{agent.title()} result"

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