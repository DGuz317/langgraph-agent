from multi_agent_system.planner.agent import PlannerAgent


def main() -> None:
    planner = PlannerAgent(
        use_llm=True,
        fallback_to_deterministic=False,
    )

    cases = [
        "Get latest invoice for customer_id=5",
        "Find tracks by artist AC/DC",
        "Get latest invoice for customer_id=5 and find tracks by artist AC/DC",
        "What is my latest invoice?",
        "recommend some rock tracks",
        "Check for song Rolling in the Deep",
    ]

    for case in cases:
        print("\nUSER:", case)
        print(planner.debug_raw_llm(case))


if __name__ == "__main__":
    main()