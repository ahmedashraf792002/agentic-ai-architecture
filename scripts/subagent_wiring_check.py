from deepagents import create_deep_agent
from dotenv import load_dotenv
from agents.models import build_model

load_dotenv()

STUB_PROMPT = (
    "You are a placeholder subagent. "
    "Always respond with exactly:\n"
    "stub-ok\n"
    "Do not add any explanation."
)

PLACEHOLDER_SUBAGENTS = [
    {"name": "strategy-analyst", "description": "Placeholder for E1.", "system_prompt": STUB_PROMPT},
    {"name": "business-analyst", "description": "Placeholder for E2.", "system_prompt": STUB_PROMPT},
    {"name": "code-analyzer", "description": "Placeholder for E3.", "system_prompt": STUB_PROMPT},
    {"name": "infra-analyzer", "description": "Placeholder for E4.", "system_prompt": STUB_PROMPT},
    {"name": "integration-mapper", "description": "Placeholder for E5.", "system_prompt": STUB_PROMPT},
]


def build_orchestrator():
    return create_deep_agent(
        model=build_model(),
        subagents=PLACEHOLDER_SUBAGENTS,
        system_prompt=(
            "Call each of these subagents, in this exact order, using the task tool: "
            "strategy-analyst, business-analyst, code-analyzer, infra-analyzer, "
            "integration-mapper. Report back each subagent's response."
        ),
    )


def main():
    orchestrator = build_orchestrator()
    result = orchestrator.invoke(
                {"messages": [{
                    "role": "user", 
                    "content":  """
                            Use the task tool to call each registered subagent in this order:

                            1. strategy-analyst
                            2. business-analyst
                            3. code-analyzer
                            4. infra-analyzer
                            5. integration-mapper

                            Return every response.
                            """
        }]})
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
