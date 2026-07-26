
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from archimate_types import ALL_ELEMENT_TYPES, ELEMENT_TYPES_BY_LAYER, RELATIONSHIP_TYPES

Layer = Literal["motivation", "strategy", "business", "application", "technology"]
Confidence = Literal["observed", "inferred"]


class Evidence(BaseModel):
    source_type: str
    locator: str
    excerpt: str | None = None


class Relationship(BaseModel):
    target_id: str
    type: str

    @field_validator("type")
    @classmethod
    def type_must_be_known(cls, value: str) -> str:
        if value not in RELATIONSHIP_TYPES:
            raise ValueError(
                f"relationship type {value!r} is not in the ArchiMate skill's "
                f"relationship vocabulary: {sorted(RELATIONSHIP_TYPES)}"
            )
        return value


class ModelElement(BaseModel):
    id: str
    layer: Layer
    archimate_type: str
    name: str
    documentation: str = ""
    confidence: Confidence
    evidence: list[Evidence] = Field(min_length=1)
    relationships: list[Relationship] = Field(default_factory=list)

    @field_validator("archimate_type")
    @classmethod
    def archimate_type_must_be_known(cls, value: str) -> str:
        if value not in ALL_ELEMENT_TYPES:
            raise ValueError(
                f"archimate_type {value!r} is not in the ArchiMate skill's "
                f"element type vocabulary"
            )
        return value

    @model_validator(mode="after")
    def archimate_type_must_match_layer(self) -> "ModelElement":
        valid_for_layer = ELEMENT_TYPES_BY_LAYER[self.layer]
        if self.archimate_type not in valid_for_layer:
            raise ValueError(
                f"archimate_type {self.archimate_type!r} is not valid for layer "
                f"{self.layer!r} (valid types: {sorted(valid_for_layer)})"
            )
        return self
