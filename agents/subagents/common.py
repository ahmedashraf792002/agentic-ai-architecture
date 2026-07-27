from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv

from agents.backend_config import build_backend, build_permissions
from agents.models import get_model
from agents.tools import make_add_relationship_tool, make_save_model_element_tool

load_dotenv()

SKILLS_DIR = "archimate-metamodel/SKILL.md"


def build_subagent_spec(name: str, description: str, system_prompt: str):
    return {"name": name, "description": description, "system_prompt": system_prompt}


def build_standalone_agent(
    system_prompt: str,
    system_id: str,
    evidence_root: str | Path,
    systems_root: str | Path,
    include_relationship_tool: bool = False,
):
    backend = build_backend(evidence_root, systems_root)
    permissions = build_permissions()

    tools = [make_save_model_element_tool(system_id, systems_root)]
    if include_relationship_tool:
        tools.append(make_add_relationship_tool(system_id, systems_root))

    return create_deep_agent(
        model=get_model(),
        backend=backend,
        permissions=permissions,
        tools=tools,
        skills=[SKILLS_DIR],
        system_prompt=system_prompt,
    )
