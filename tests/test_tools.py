import json
from pathlib import Path

import pytest

from agents.tools import make_add_relationship_tool, make_save_model_element_tool

SYSTEM_ID = "test-system"


@pytest.fixture()
def systems_root(tmp_path: Path):
    return tmp_path / "systems"


def valid_element_kwargs(**overrides):
    base = dict(
        id="app-payment-service",
        layer="application",
        archimate_type="Application Service",
        name="Payment Service",
        documentation="Handles payment authorization.",
        confidence="observed",
        evidence=[{"source_type": "code", "locator": "src/payments/service.py:12-40"}],
        relationships=[],
    )
    base.update(overrides)
    return base


def test_save_model_element_writes_valid_file(systems_root: Path):
    save_tool = make_save_model_element_tool(SYSTEM_ID, systems_root)
    result = save_tool.invoke(valid_element_kwargs())

    out_path = systems_root / SYSTEM_ID / "as-is" / "application" / "app-payment-service.json"
    assert out_path.exists()
    assert "Saved" in result

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["archimate_type"] == "Application Service"


def test_save_model_element_rejects_empty_evidence(systems_root: Path):
    save_tool = make_save_model_element_tool(SYSTEM_ID, systems_root)
    result = save_tool.invoke(valid_element_kwargs(evidence=[]))

    assert "REJECTED" in result
    out_path = systems_root / SYSTEM_ID / "as-is" / "application" / "app-payment-service.json"
    assert not out_path.exists()


def test_save_model_element_rejects_unknown_archimate_type(systems_root: Path):
    save_tool = make_save_model_element_tool(SYSTEM_ID, systems_root)
    result = save_tool.invoke(valid_element_kwargs(archimate_type="Not A Real Type"))

    assert "REJECTED" in result


def test_add_relationship_succeeds_when_both_ids_exist(systems_root: Path):
    save_tool = make_save_model_element_tool(SYSTEM_ID, systems_root)
    save_tool.invoke(valid_element_kwargs(id="app-payment-service"))
    save_tool.invoke(
        valid_element_kwargs(
            id="biz-checkout-process",
            layer="business",
            archimate_type="Business Process",
            evidence=[{"source_type": "docs", "locator": "checkout.md"}],
        )
    )

    add_relationship = make_add_relationship_tool(SYSTEM_ID, systems_root)
    result = add_relationship.invoke(
        {
            "source_element_id": "app-payment-service",
            "target_element_id": "biz-checkout-process",
            "relationship_type": "Serving",
        }
    )
    assert "Added" in result

    saved = json.loads(
        (systems_root / SYSTEM_ID / "as-is" / "application" / "app-payment-service.json").read_text()
    )
    assert saved["relationships"] == [{"target_id": "biz-checkout-process", "type": "Serving"}]


def test_add_relationship_rejects_nonexistent_target(systems_root: Path):
    save_tool = make_save_model_element_tool(SYSTEM_ID, systems_root)
    save_tool.invoke(valid_element_kwargs(id="app-payment-service"))

    add_relationship = make_add_relationship_tool(SYSTEM_ID, systems_root)
    result = add_relationship.invoke(
        {
            "source_element_id": "app-payment-service",
            "target_element_id": "does-not-exist",
            "relationship_type": "Serving",
        }
    )
    assert "REJECTED" in result
    saved = json.loads(
        (systems_root / SYSTEM_ID / "as-is" / "application" / "app-payment-service.json").read_text()
    )
    assert saved["relationships"] == []  


def test_add_relationship_rejects_nonexistent_source(systems_root: Path):
    add_relationship = make_add_relationship_tool(SYSTEM_ID, systems_root)
    result = add_relationship.invoke(
        {
            "source_element_id": "does-not-exist",
            "target_element_id": "also-does-not-exist",
            "relationship_type": "Serving",
        }
    )
    assert "REJECTED" in result
