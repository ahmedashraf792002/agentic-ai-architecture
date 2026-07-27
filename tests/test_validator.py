import json
from pathlib import Path

from agents.validator import validate, write_validation_report

SYSTEM_ID = "test-system"


def write_raw(systems_root: Path, element_id: str, layer: str, data_overrides: dict):
    out_dir = systems_root / SYSTEM_ID / "as-is" / layer
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{element_id}.json"
    base = {
        "id": element_id,
        "layer": layer,
        "archimate_type": "Application Service",
        "name": "Payment Service",
        "documentation": "",
        "confidence": "observed",
        "evidence": [{"source_type": "docs", "locator": "x.md"}],
        "relationships": [],
    }
    base.update(data_overrides)
    path.write_text(json.dumps(base), encoding="utf-8")
    return path


def test_validate_passes_clean_input(tmp_path: Path):
    write_raw(tmp_path, "app-1", "application", {})

    report = validate(tmp_path, SYSTEM_ID)

    assert report.passed is True
    assert report.violations == []
    assert report.counts_by_layer["application"] == 1


def test_validate_flags_invalid_archimate_type(tmp_path: Path):
    write_raw(tmp_path, "app-1", "application", {"archimate_type": "Not A Real Type"})

    report = validate(tmp_path, SYSTEM_ID)

    assert report.passed is False
    assert len(report.violations) == 1


def test_validate_flags_illegal_relationship_type(tmp_path: Path):
    write_raw(tmp_path, "app-1", "application", {})
    write_raw(
        tmp_path,
        "app-2",
        "application",
        {"relationships": [{"target_id": "app-1", "type": "NotARealRelationship"}]},
    )

    report = validate(tmp_path, SYSTEM_ID)

    assert report.passed is False
    assert any("app-2" in v["path"] for v in report.violations)


def test_validate_flags_dangling_relationship_target(tmp_path: Path):
    write_raw(
        tmp_path,
        "app-1",
        "application",
        {"relationships": [{"target_id": "does-not-exist", "type": "Serving"}]},
    )

    report = validate(tmp_path, SYSTEM_ID)

    assert report.passed is False
    assert any("unknown id" in v["error"] for v in report.violations)


def test_validate_flags_missing_evidence(tmp_path: Path):
    write_raw(tmp_path, "app-1", "application", {"evidence": []})

    report = validate(tmp_path, SYSTEM_ID)

    assert report.passed is False
    assert any("app-1" in v["path"] for v in report.violations)


def test_validate_flags_needs_review_for_cross_type_composition(tmp_path: Path):
    write_raw(tmp_path, "app-1", "application", {"archimate_type": "Application Component"})
    write_raw(
        tmp_path,
        "app-2",
        "application",
        {
            "archimate_type": "Application Service",
            "relationships": [{"target_id": "app-1", "type": "Composition"}],
        },
    )

    report = validate(tmp_path, SYSTEM_ID)

    assert report.passed is True
    assert len(report.needs_review) == 1


def test_write_validation_report(tmp_path: Path):
    write_raw(tmp_path, "app-1", "application", {})
    report = validate(tmp_path, SYSTEM_ID)
    report_path = write_validation_report(tmp_path, SYSTEM_ID, report)

    assert report_path.exists()
    data = json.loads(report_path.read_text())
    assert data["passed"] is True
