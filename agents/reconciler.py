import re
import json
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

from agents.schema import ModelElement

SIMILARITY_THRESHOLD: float = 0.82


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower())


@dataclass
class ReconciliationResult:
    merged_count: int = 0
    conflicts: list[dict] = field(default_factory=list)

    def to_dict(self):
        return {"merged_count": self.merged_count, "conflicts": self.conflicts}


def load_elements(systems_root: str | Path, system_id: str):
    system_dir = Path(systems_root) / system_id / "as-is"
    if not system_dir.exists():
        return []
    return [
        (path, ModelElement.model_validate_json(path.read_text(encoding="utf-8")))
        for path in sorted(system_dir.glob("*/*.json"))
    ]


def merge_elements(primary: ModelElement, duplicate: ModelElement):
    evidence = primary.evidence + [e for e in duplicate.evidence if e not in primary.evidence]
    relationships = primary.relationships + [
        r for r in duplicate.relationships if r not in primary.relationships
    ]
    return primary.model_copy(update={"evidence": evidence, "relationships": relationships})


def reconcile(systems_root: str | Path, system_id: str):
    systems_root = Path(systems_root)
    elements = load_elements(systems_root, system_id)
    result = ReconciliationResult()

    groups: dict[tuple[str, str], list[tuple[Path, ModelElement]]] = {}
    for path, element in elements:
        groups.setdefault((element.layer, element.archimate_type), []).append((path, element))

    for (layer, archimate_type), group in groups.items():
        merged_indices: set[int] = set()
        for i in range(len(group)):
            if i in merged_indices:
                continue
            path_i, element_i = group[i]
            name_i = normalize_name(element_i.name)

            for j in range(i + 1, len(group)):
                if j in merged_indices:
                    continue
                path_j, element_j = group[j]
                name_j = normalize_name(element_j.name)

                if name_i == name_j:
                    element_i = merge_elements(element_i, element_j)
                    path_i.write_text(element_i.model_dump_json(indent=2), encoding="utf-8")
                    path_j.unlink()
                    merged_indices.add(j)
                    result.merged_count += 1
                    continue

                ratio = SequenceMatcher(None, name_i, name_j).ratio()
                if SIMILARITY_THRESHOLD <= ratio < 1.0:
                    result.conflicts.append(
                        {
                            "layer": layer,
                            "archimate_type": archimate_type,
                            "element_a": {"id": element_i.id, "name": element_i.name, "path": str(path_i)},
                            "element_b": {"id": element_j.id, "name": element_j.name, "path": str(path_j)},
                            "similarity": round(ratio, 3),
                        }
                    )

    return result


def write_reconciliation_report(
    systems_root: str | Path, system_id: str, result: ReconciliationResult
) :

    out_dir = Path(systems_root) / system_id / "as-is" / "_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "reconciliation-report.json"
    out_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    return out_path
