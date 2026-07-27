import json
from pathlib import Path
from agents.reconciler import reconcile, write_reconciliation_report

SYSTEM_ID = "test-system"


def write_element(systems_root: Path, element_id: str, layer: str, archimate_type: str, name: str):
    out_dir = systems_root / SYSTEM_ID / "as-is" / layer
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{element_id}.json"
    data = {
        "id": element_id,
        "layer": layer,
        "archimate_type": archimate_type,
        "name": name,
        "documentation": "",
        "confidence": "observed",
        "evidence": [{"source_type": "docs", "locator": f"{element_id}.md"}],
        "relationships": [],
    }
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_reconcile_merges_exact_normalized_duplicate(tmp_path: Path):
    write_element(tmp_path, "app-payment-service", "application", "Application Service", "Payment Service")
    write_element(tmp_path, "app-payment-svc-dup", "application", "Application Service", "payment-service!!")

    result = reconcile(tmp_path, SYSTEM_ID)

    assert result.merged_count == 1
    remaining = list((tmp_path / SYSTEM_ID / "as-is" / "application").glob("*.json"))
    assert len(remaining) == 1

    merged = json.loads(remaining[0].read_text())
    assert len(merged["evidence"]) == 2


def test_reconcile_flags_ambiguous_near_miss_as_conflict(tmp_path: Path):
    write_element(tmp_path, "app-payment-service", "application", "Application Service", "Payment Service")
    write_element(tmp_path, "app-payment-processing", "application", "Application Service", "Payment Processing")

    result = reconcile(tmp_path, SYSTEM_ID)

    assert result.merged_count == 0
    remaining = list((tmp_path / SYSTEM_ID / "as-is" / "application").glob("*.json"))
    assert len(remaining) == 2


def test_reconcile_does_not_merge_across_archimate_type(tmp_path: Path):
    write_element(tmp_path, "app-payment-service", "application", "Application Service", "Payment Service")
    write_element(tmp_path, "app-payment-service-comp", "application", "Application Component", "Payment Service")

    result = reconcile(tmp_path, SYSTEM_ID)

    assert result.merged_count == 0


def test_write_reconciliation_report(tmp_path: Path):
    write_element(tmp_path, "app-payment-service", "application", "Application Service", "Payment Service")
    result = reconcile(tmp_path, SYSTEM_ID)
    report_path = write_reconciliation_report(tmp_path, SYSTEM_ID, result)

    assert report_path.exists()
    data = json.loads(report_path.read_text())
    assert "merged_count" in data
    assert "conflicts" in data
