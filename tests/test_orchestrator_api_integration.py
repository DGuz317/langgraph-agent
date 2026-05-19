import os

import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_ORCHESTRATOR_API_INTEGRATION_TESTS") != "1",
    reason=(
        "Set RUN_ORCHESTRATOR_API_INTEGRATION_TESTS=1, configure .env, "
        "and start MCP plus both A2A services to run planner API integration tests."
    ),
)


def test_real_planner_api_completes_invoice_flow() -> None:
    from fastapi.testclient import TestClient

    from multi_agent_system.orchestrator.server import create_app

    client = TestClient(create_app())

    response = client.post(
        "/planner/invoke",
        json={
            "user_input": "Get latest invoice for customer_id=5",
            "thread_id": "integration-invoice-thread",
        },
    )

    body = response.json()

    assert response.status_code == 200, body
    assert body["status"] == "completed", body
    assert body["thread_id"] == "integration-invoice-thread"
    assert body["needs_resume"] is False
    assert body["final_answer"]
    assert "failed" not in body["final_answer"].lower()
    assert "invoice" in body["final_answer"].lower()


def test_real_planner_api_interrupts_and_resumes_invoice_flow() -> None:
    from fastapi.testclient import TestClient

    from multi_agent_system.orchestrator.server import create_app

    client = TestClient(create_app())

    interrupted = client.post(
        "/planner/invoke",
        json={
            "user_input": "What is my latest invoice?",
            "thread_id": "integration-hitl-thread",
        },
    )

    interrupted_body = interrupted.json()

    assert interrupted.status_code == 200, interrupted_body
    assert interrupted_body["status"] == "interrupted", interrupted_body
    assert interrupted_body["thread_id"] == "integration-hitl-thread"
    assert interrupted_body["needs_resume"] is True
    assert interrupted_body["interrupt_message"]

    completed = client.post(
        "/planner/invoke",
        json={
            "user_input": "5",
            "thread_id": interrupted_body["thread_id"],
            "resume": True,
        },
    )

    completed_body = completed.json()

    assert completed.status_code == 200, completed_body
    assert completed_body["status"] == "completed", completed_body
    assert completed_body["thread_id"] == "integration-hitl-thread"
    assert completed_body["needs_resume"] is False
    assert completed_body["final_answer"]
    assert "failed" not in completed_body["final_answer"].lower()
    assert "invoice" in completed_body["final_answer"].lower()
