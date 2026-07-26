from deepagents import create_deep_agent
from agents.models import build_model

SKILL_PATH = "archimate-metamodel/SKILL.md"

QUESTIONS = [
    # Motivation
    "What layer does Goal belong to?",

    # Strategy
    "What is a Capability?",

    # Business
    "What layer does Business Process belong to?",

    # Application
    "What layer does Application Interface belong to?",

    # Technology
    "What is a Technology Service?",

    # Relationships
    "Is Assignment valid between Business Actor and Business Process?",

    "Can an Application Service serve a Business Process?",

    "Is Realization valid from Business Process to Technology Node?",
]

def build_agent():
    return create_deep_agent(
        model=build_model(),
        skills=[SKILL_PATH],
        system_prompt=(
            "Answer only using the loaded SKILL.md."
            "Do not search the repository."
            "Do not use any tools."
            "Is Assignment valid between Business Actor and Business Process?"
         )
    )

def main():
    agent = build_agent()

    print("=" * 80)
    print("ArchiMate Skill Smoke Test")
    print("=" * 80)

    for i, question in enumerate(QUESTIONS, start=1):
        print(f"\nQuestion {i}")
        print(question)

        response = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": question,
                    }
                ]
            }
        )

        print("\nAnswer")
        print(response["messages"][-1].content)


if __name__ == "__main__":
    main()