import os
from contextlib import suppress
from uuid import uuid4

import pytest

from acontext import AcontextAsyncClient
from acontext.errors import APIError, TransportError

from multi_agent_system.config import settings
from multi_agent_system.orchestrator.acontext_capture import (
    AcontextCapture,
    acontext_session_id,
)
from multi_agent_system.orchestrator.schemas import PlannerServiceResponse


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_ACONTEXT_INTEGRATION_TESTS") != "1",
    reason=(
        "Set RUN_ACONTEXT_INTEGRATION_TESTS=1, enable Acontext in .env, and "
        "start its local API with a learning model to run skill-memory tests."
    ),
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_visible_chat_session_reaches_learning_terminal_state() -> None:
    assert settings.acontext_api_key
    api_key = settings.acontext_api_key
    base_url = settings.acontext_base_url
    run_id = str(uuid4())
    user_identifier = f"multi-agent-integration-{run_id}"
    thread_id = f"acontext-test-{run_id}"
    space_id: str | None = None
    learned_skill_ids: list[str] = []

    capture = AcontextCapture(
        api_key=api_key,
        base_url=base_url,
        user_identifier=user_identifier,
    )
    response = PlannerServiceResponse(
        status="completed",
        thread_id=thread_id,
        final_answer=(
            "Completed project convention update. "
            "Reusable rule: In this multi-agent system, invoice requests with "
            "customer_id must be routed to the invoice agent. The planner should "
            "preserve customer_id in task args and build an instruction such as "
            "'Get latest invoice for customer_id=5'."
        ),
    )

    try:
        await capture.capture(
            user_input=(
                "Remember this project convention: invoice requests with customer_id "
                "must be routed to the invoice agent, and customer_id must be preserved "
                "in task args."
            ),
            thread_id=thread_id,
            resume=False,
            response=response,
        )

        async with AcontextAsyncClient(
            api_key=api_key,
            base_url=base_url,
        ) as client:
            spaces = await client.learning_spaces.list(
                user=user_identifier,
                filter_by_meta={
                    "source": "multi_agent_system.planner",
                    "memory_scope": "visible-chat-v1",
                },
            )
            assert spaces.items
            space_id = spaces.items[0].id

            learning = await client.learning_spaces.wait_for_learning(
                space_id,
                session_id=acontext_session_id(thread_id),
                timeout=1000,
            )
            if learning.status != "completed":
                if hasattr(learning, "model_dump"):
                    print("learning:", learning.model_dump())
                else:
                    print("learning:", repr(learning))

            assert learning.status == "completed"

            skills = await client.learning_spaces.list_skills(space_id)
            learned_skill_ids = [skill.id for skill in skills]
    finally:
        async with AcontextAsyncClient(
            api_key=api_key,
            base_url=base_url,
        ) as client:
            with suppress(APIError, TransportError):
                await client.sessions.delete(acontext_session_id(thread_id))
            if space_id is not None:
                with suppress(APIError, TransportError):
                    await client.learning_spaces.delete(space_id)
            for skill_id in learned_skill_ids:
                with suppress(APIError, TransportError):
                    await client.skills.delete(skill_id)
