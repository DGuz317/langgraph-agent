import asyncio
import uuid

from agent_app.agents.invoice_agent import init_invoice_agent
from agent_app.agents.music_agent import init_music_agent
from agent_app.agents.planner_agent import init_planner_agent
from agent_app.agents.orchestrator import run_session


# ---------------------------------------------------------------------------
# Startup — must run before any session
# ---------------------------------------------------------------------------

async def startup():
    """
    Initialize all agents in order.
    MCP server must already be running before this is called.

    Order matters:
      1. invoice_agent  — connects to MCP, loads invoice tools
      2. music_agent    — connects to MCP, loads music tools
      3. planner_agent  — no MCP needed, just model + response format
    """
    print("Starting up agents...")

    await init_invoice_agent()
    print("  ✅ invoice_agent ready")

    await init_music_agent()
    print("  ✅ music_agent ready")

    await init_planner_agent()
    print("  ✅ planner_agent ready")

    print("\nAll agents initialized. Orchestrator ready.\n")


# ---------------------------------------------------------------------------
# Test sessions
# ---------------------------------------------------------------------------

async def test_single_task():
    """Music query — single task, no aggregation needed."""
    print("=" * 50)
    print("TEST: Single task (music)")
    print("=" * 50)

    thread_id = str(uuid.uuid4())
    result = await run_session(
        "Get me all tracks by AC/DC",
        thread_id=thread_id,
    )
    print("Answer:", result["final_answer"])
    print()


async def test_multi_task():
    """Both music and invoice — two tasks, aggregation needed."""
    print("=" * 50)
    print("TEST: Multi task (music + invoice)")
    print("=" * 50)

    thread_id = str(uuid.uuid4())
    result = await run_session(
        "Show me AC/DC songs and my invoices sorted by price, my customer id is 5",
        thread_id=thread_id,
    )
    print("Answer:", result["final_answer"])
    print()


async def test_missing_info():
    """
    Invoice query with no customer ID.
    Turn 1 → ask_user returns clarification.
    Turn 2 → user provides ID, invoice is fetched.
    """
    print("=" * 50)
    print("TEST: Missing info (multi-turn)")
    print("=" * 50)

    thread_id = str(uuid.uuid4())

    # Turn 1 — missing customer ID
    result = await run_session(
        "What are my invoices?",
        thread_id=thread_id,
    )
    print("Bot (turn 1):", result["final_answer"])

    # Turn 2 — user provides the ID
    result = await run_session(
        "My customer id is 3",
        history=result["messages"],
        thread_id=thread_id,
    )
    print("Bot (turn 2):", result["final_answer"])
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main():
    await startup()

    # await test_single_task()
    await test_multi_task()
    await test_missing_info()


if __name__ == "__main__":
    asyncio.run(main())