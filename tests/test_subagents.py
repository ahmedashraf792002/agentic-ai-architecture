from pathlib import Path

from agents.subagents.strategy_analyst import build_standalone as build_strategy
from agents.subagents.business_analyst import build_standalone as build_business
from agents.subagents.code_analyzer import build_standalone as build_code
from agents.subagents.infra_analyzer import build_standalone as build_infra
from agents.subagents.integration_mapper import build_standalone as build_integration

SYSTEM_ID = "sample-system"
EVIDENCE_ROOT = Path("evidence")
SYSTEMS_ROOT = Path("systems")


PROMPT = """
Analyze all available evidence and produce the corresponding ArchiMate
elements (or relationships, if applicable) according to your system prompt.
"""


def run_agent(name: str, builder):
    print(f"\n========== Running {name} ==========")

    agent = builder(
        system_id=SYSTEM_ID,
        evidence_root=EVIDENCE_ROOT,
        systems_root=SYSTEMS_ROOT,
    )

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": PROMPT,
                }
            ]
        }
    )

    print(result)


def main():
    run_agent("strategy-analyst", build_strategy)
    run_agent("business-analyst", build_business)
    run_agent("code-analyzer", build_code)
    run_agent("infra-analyzer", build_infra)
    run_agent("integration-mapper", build_integration)


if __name__ == "__main__":
    main()