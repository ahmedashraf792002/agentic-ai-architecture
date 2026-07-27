import json
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import ValidationError

from agents.schema import ModelElement

SAME_TYPE_ONLY_RELATIONSHIPS = {"Composition", "Aggregation", "Specialization"}


@dataclass
class ValidationReport:
    counts_by_layer: dict[str, int] = field(default_factory=dict)
    violations: list[dict] = field(default_factory=list)
    needs_review: list[dict] = field(default_factory=list)
    passed: bool = True

    def to_dict(self):
        return {
            "counts_by_layer": self.counts_by_layer,
            "violations": self.violations,
            "needs_review": self.needs_review,
            "passed": self.passed,
        }


def load_raw_elements(systems_root: str | Path, system_id: str):
    system_dir = Path(systems_root) / system_id / "as-is"
    if not system_dir.exists():
        return []
    return [
        (path, json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(system_dir.glob("*/*.json"))
    ]


def validate(systems_root: str | Path, system_id: str):
    report = ValidationReport()
    raw_elements = load_raw_elements(systems_root, system_id)

    known = {raw["id"]: raw for _, raw in raw_elements if "id" in raw}

    for path, raw in raw_elements:
        try:
            element = ModelElement.model_validate(raw)
        except ValidationError as exc:
            report.violations.append({"path": str(path), "error": str(exc)})
            report.passed = False
            continue

        report.counts_by_layer[element.layer] = report.counts_by_layer.get(element.layer, 0) + 1

        for relationship in element.relationships:
            if relationship.target_id not in known:
                report.violations.append(
                    {
                        "path": str(path),
                        "error": f"relationship targets unknown id {relationship.target_id!r}",
                    }
                )
                report.passed = False
                continue

            if relationship.type in SAME_TYPE_ONLY_RELATIONSHIPS:
                target_type = known[relationship.target_id].get("archimate_type")
                if target_type != element.archimate_type:
                    report.needs_review.append(
                        {
                            "path": str(path),
                            "reason": (
                                f"{relationship.type} from {element.archimate_type!r} to "
                                f"{target_type!r} is not covered by the skill's universal "
                                "same-type rule; needs SME confirmation"
                            ),
                        }
                    )

    return report


def write_validation_report(systems_root: str | Path, system_id: str, report: ValidationReport):
    out_dir = Path(systems_root) / system_id / "as-is" / "_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "validation-report.json"
    out_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    return out_path
