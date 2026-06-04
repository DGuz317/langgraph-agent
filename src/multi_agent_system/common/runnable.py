from __future__ import annotations

from typing import Any


async def ainvoke_with_optional_config(
    runnable: Any,
    input_value: Any,
    *,
    config: dict[str, Any],
) -> Any:
    try:
        return await runnable.ainvoke(input_value, config=config)
    except TypeError as exc:
        if "config" not in str(exc):
            raise
        return await runnable.ainvoke(input_value)
