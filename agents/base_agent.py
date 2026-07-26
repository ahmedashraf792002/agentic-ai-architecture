from pathlib import Path

from deepagents import create_deep_agent
#from deepagents.middleware import TodoListMiddleware

from backend_config import build_backend, build_permissions
from models import build_model

PROJECT_ROOT = Path(__file__).resolve().parent.parent



def build_base_agent(evidence_root: str | Path, systems_root: str | Path):
    backend = build_backend(
        evidence_root=evidence_root,
        systems_root=systems_root,
    )

    permissions = build_permissions()

    agent = create_deep_agent(
        model=build_model(),
        backend=backend,
        permissions=permissions,
        middleware=[
            #TodoListMiddleware(),
        ],
    )

    return agent
if __name__ == "__main__":
    print("Testing Base Deep Agent...")
    agent = build_base_agent(evidence_root="./evidence", systems_root="./systems")
    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello!",
                }
            ]
        }
    )

    print("\nAgent Response:")
    for msg in response["messages"]:
        print("=" * 40)
        print(type(msg).__name__)
        print(msg.content)