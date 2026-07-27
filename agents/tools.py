import logging
from pathlib import Path

from langchain_core.tools import tool
from pydantic import ValidationError

from agents.schema import Evidence, ModelElement, Relationship

logger = logging.getLogger(__name__)


def _layer_dir(systems_root: Path, system_id: str, layer: str):
    return Path(systems_root) / system_id / "as-is" / layer


def _element_path(systems_root: Path, system_id: str, layer: str, element_id: str):
    return _layer_dir(systems_root, system_id, layer) / f"{element_id}.json"


def _find_element_path(systems_root: Path, system_id: str, element_id: str):
    
    system_dir = Path(systems_root) / system_id / "as-is"
    if not system_dir.exists():
        return None
    for candidate in system_dir.glob(f"*/{element_id}.json"):
        return candidate
    return None


def make_save_model_element_tool(system_id: str, systems_root: str | Path):
    systems_root = Path(systems_root)

    @tool
    def save_model_element(
        id: str,
        layer: str,
        archimate_type: str,
        name: str,
        documentation: str,
        confidence: str,
        evidence: list[dict],
        relationships: list[dict] | None = None,
    ) :
        try:
            element = ModelElement(
                id=id,
                layer=layer,  
                archimate_type=archimate_type,
                name=name,
                documentation=documentation,
                confidence=confidence,  
                evidence=[Evidence(**e) for e in evidence],
                relationships=[Relationship(**r) for r in (relationships or [])],
            )
        except ValidationError as exc:
            logger.warning("save_model_element rejected id=%s: %s", id, exc)
            return f"REJECTED — not written. Schema validation failed:\n{exc}"

        out_path = _element_path(systems_root, system_id, element.layer, element.id)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(element.model_dump_json(indent=2), encoding="utf-8")
        logger.info("saved element id=%s layer=%s -> %s", element.id, element.layer, out_path)
        return f"Saved {element.archimate_type} '{element.name}' -> {out_path}"

    return save_model_element


def make_add_relationship_tool(system_id: str, systems_root: str | Path):
    systems_root = Path(systems_root)

    @tool
    def add_relationship(source_element_id: str, target_element_id: str, relationship_type: str):

        source_path = _find_element_path(systems_root, system_id, source_element_id)
        if source_path is None:
            return f"REJECTED — source element id {source_element_id!r} does not exist."

        target_path = _find_element_path(systems_root, system_id, target_element_id)
        if target_path is None:
            return (
                f"REJECTED — target element id {target_element_id!r} does not exist yet. "
                "This is a bug, not a valid inferred relationship — do not invent it."
            )

        try:
            source = ModelElement.model_validate_json(source_path.read_text(encoding="utf-8"))
            source.relationships.append(
                Relationship(target_id=target_element_id, type=relationship_type)
            )
        except ValidationError as exc:
            return f"REJECTED — relationship failed schema validation:\n{exc}"

        source_path.write_text(source.model_dump_json(indent=2), encoding="utf-8")
        return f"Added {relationship_type} relationship: {source_element_id} -> {target_element_id}"

    return add_relationship
