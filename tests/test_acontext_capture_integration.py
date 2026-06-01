import os
from contextlib import suppress
from uuid import uuid4

import pytest

from acontext import AcontextAsyncClient
from acontext.errors import APIError, TransportError

from multi_agent_system.common.execution_evidence import ExecutionEvidence
from multi_agent_system.config import settings
from multi_agent_system.orchestrator.acontext_capture import (
    AcontextCapture,
    acontext_session_id,
)
from multi_agent_system.orchestrator.acontext_common import MEMORY_SCOPE
from multi_agent_system.orchestrator.schemas import PlannerServiceResponse


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_ACONTEXT_INTEGRATION_TESTS") != "1",
    reason=(
        "Set RUN_ACONTEXT_INTEGRATION_TESTS=1, enable Acontext in .env, and "
        "start its local API with a learning model to run skill-memory tests."
    ),
)
requires_learning_wait = pytest.mark.skipif(
    os.getenv("RUN_ACONTEXT_LEARNING_INTEGRATION_TESTS") != "1",
    reason=(
        "Set RUN_ACONTEXT_LEARNING_INTEGRATION_TESTS=1 to run slow Acontext "
        "learning-completion checks."
    ),
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
@requires_learning_wait
async def test_direct_acontext_learning_after_flush() -> None:
    assert settings.acontext_api_key
    api_key = settings.acontext_api_key
    base_url = settings.acontext_base_url
    user_identifier = f"manual-learning-{uuid4()}"
    space_id: str | None = None
    session_id: str | None = None
    learned_skill_ids: list[str] = []

    try:
        async with AcontextAsyncClient(
            api_key=api_key,
            base_url=base_url,
            timeout=settings.acontext_timeout,
        ) as client:
            space = await client.learning_spaces.create(
                user=user_identifier,
                meta={
                    "source": "manual-test",
                    "memory_scope": "debug-learning-v1",
                },
            )
            space_id = space.id

            session = await client.sessions.create(user=user_identifier)
            session_id = session.id

            await client.sessions.store_message(
                session.id,
                blob={
                    "role": "user",
                    "content": (
                        "Remember this project rule: invoice requests with customer_id "
                        "must route to the invoice agent. The planner must preserve "
                        "customer_id in the natural-language task instruction."
                    ),
                },
            )
            await client.sessions.store_message(
                session.id,
                blob={
                    "role": "assistant",
                    "content": (
                        "Rule saved. Reusable convention: when the user asks for invoices "
                        "and provides customer_id, create an invoice task instruction "
                        "like 'Get latest invoice for customer_id=5'."
                    ),
                },
            )

            await client.sessions.flush(session.id)
            await client.learning_spaces.learn(space.id, session_id=session.id)

            learning = await client.learning_spaces.wait_for_learning(
                space.id,
                session_id=session.id,
                timeout=settings.acontext_timeout,
            )
            assert learning.status == "completed", f"learning={learning!r}"

            skills = await client.learning_spaces.list_skills(space.id)
            learned_skill_ids = [skill.id for skill in skills]
    finally:
        async with AcontextAsyncClient(
            api_key=api_key,
            base_url=base_url,
            timeout=settings.acontext_timeout,
        ) as client:
            if session_id is not None:
                with suppress(APIError, TransportError):
                    await client.sessions.delete(session_id)
            if space_id is not None:
                with suppress(APIError, TransportError):
                    await client.learning_spaces.delete(space_id)
            for skill_id in learned_skill_ids:
                with suppress(APIError, TransportError):
                    await client.skills.delete(skill_id)


@pytest.mark.anyio
async def test_workflow_outcome_session_is_stored_and_flushed() -> None:
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
        timeout=settings.acontext_timeout,
    )
    response = PlannerServiceResponse(
        status="completed",
        thread_id=thread_id,
        final_answer=(
            "Completed project convention update. "
            "Reusable rule: In this multi-agent system, invoice requests with "
            "customer_id must be routed to the invoice agent. The planner should "
            "preserve customer_id in the task instruction, such as "
            "'Get latest invoice for customer_id=5'."
        ),
        raw_result={
            "planner_output": {
                "tasks": [
                    {
                        "agent": "invoice",
                        "status": "completed",
                        "instruction": "Get latest invoice for customer_id=5",
                    }
                ],
            },
            "execution_evidence": [
                ExecutionEvidence(
                    kind="planner_decision",
                    agent="planner",
                    operation="invoice",
                    status="completed",
                    summary="Planner selected an executable agent dispatch.",
                ).model_dump(),
                ExecutionEvidence(
                    kind="agent_result",
                    agent="invoice",
                    operation="agent_instruction",
                    status="completed",
                    summary="Domain agent completed the instruction.",
                ).model_dump(),
            ]
        },
    )

    try:
        await capture.capture(
            user_input=(
                "Remember this project convention: invoice requests with customer_id "
                "must be routed to the invoice agent, and customer_id must be preserved "
                "in the task instruction."
            ),
            thread_id=thread_id,
            resume=False,
            response=response,
        )

        async with AcontextAsyncClient(
            api_key=api_key,
            base_url=base_url,
            timeout=settings.acontext_timeout,
        ) as client:
            spaces = await client.learning_spaces.list(
                user=user_identifier,
                filter_by_meta={
                    "source": "multi_agent_system.planner",
                    "memory_scope": MEMORY_SCOPE,
                },
            )
            assert spaces.items
            space_id = spaces.items[0].id
            messages = await client.sessions.get_messages(
                acontext_session_id(thread_id),
                format="openai",
            )
            serialized_messages = str(messages.items)
            assert "customer_id=5" in serialized_messages
            assert "Remember this project convention" in serialized_messages

            if os.getenv("RUN_ACONTEXT_LEARNING_INTEGRATION_TESTS") == "1":
                learning = await client.learning_spaces.wait_for_learning(
                    space_id,
                    session_id=acontext_session_id(thread_id),
                    timeout=settings.acontext_timeout,
                )
                assert learning.status == "completed"

                skills = await client.learning_spaces.list_skills(space_id)
                learned_skill_ids = [skill.id for skill in skills]
    finally:
        async with AcontextAsyncClient(
            api_key=api_key,
            base_url=base_url,
            timeout=settings.acontext_timeout,
        ) as client:
            with suppress(APIError, TransportError):
                await client.sessions.delete(acontext_session_id(thread_id))
            if space_id is not None:
                with suppress(APIError, TransportError):
                    await client.learning_spaces.delete(space_id)
            for skill_id in learned_skill_ids:
                with suppress(APIError, TransportError):
                    await client.skills.delete(skill_id)
