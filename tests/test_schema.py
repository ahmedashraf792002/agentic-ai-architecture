import pytest
from pydantic import ValidationError

from agents.schema import Evidence, ModelElement, Relationship


def make_valid_element(**overrides) -> dict:
    base = dict(
        id="app-payment-service",
        layer="application",
        archimate_type="Application Service",
        name="Payment Service",
        documentation="Handles payment authorization.",
        confidence="observed",
        evidence=[Evidence(source_type="code", locator="src/payments/service.py:12-40")],
        relationships=[],
    )
    base.update(overrides)
    return base


def test_valid_element_passes():
    element = ModelElement(**make_valid_element())
    assert element.archimate_type == "Application Service"


def test_empty_evidence_fails_validation():
    with pytest.raises(ValidationError):
        ModelElement(**make_valid_element(evidence=[]))


def test_unknown_archimate_type_fails_validation():
    with pytest.raises(ValidationError):
        ModelElement(**make_valid_element(archimate_type="Not A Real Type"))


def test_archimate_type_from_wrong_layer_fails_validation():
    # "Business Process" is a real ArchiMate type, but not valid for layer="application"
    with pytest.raises(ValidationError):
        ModelElement(**make_valid_element(layer="application", archimate_type="Business Process"))


def test_unknown_relationship_type_fails_validation():
    with pytest.raises(ValidationError):
        ModelElement(
            **make_valid_element(
                relationships=[Relationship(target_id="biz-process-1", type="Not A Real Relationship")]
            )
        )


def test_known_relationship_type_passes():
    element = ModelElement(
        **make_valid_element(
            relationships=[Relationship(target_id="biz-process-1", type="Serving")]
        )
    )
    assert element.relationships[0].type == "Serving"
