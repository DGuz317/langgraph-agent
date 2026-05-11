from multi_agent_system.planner.agent import PlannerAgent


def run_case(text: str) -> None:
    planner = PlannerAgent(
        use_llm=True,
        fallback_to_deterministic=False,
    )

    output = planner.invoke(text)

    print("\nUSER:", text)
    print(output.model_dump_json(indent=2))


def main() -> None:
    run_case("Get latest invoice for customer_id=5")
    run_case("Find tracks by artist AC/DC")
    run_case("Get latest invoice for customer_id=5 and find tracks by artist AC/DC")
    run_case("What is my latest invoice?")
    run_case("recommend some rock tracks")
    run_case("Check for song Rolling in the Deep")


if __name__ == "__main__":
    main()