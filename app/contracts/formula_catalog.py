from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


def _require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")


def _require_non_empty_items(values: list[str], field_name: str) -> None:
    if any(not isinstance(item, str) or not item.strip() for item in values):
        raise ValueError(f"{field_name} cannot contain empty strings")


class FormulaCatalogEntry(BaseModel):
    """Governed deterministic formula definition from formula_catalog.

    The LLM may map evidence to required inputs, but it must not define or alter
    the formula semantics. This contract stores the inputs and operating limits
    required before the math kernel can run a calculation.
    """

    formula_id: str
    name: str
    description: str
    required_inputs: list[str] = Field(..., min_length=1)
    accepted_sources: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    unit: str | None = None
    period: str | None = None
    when_not_to_use: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    allows_tenant_override: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate(self) -> "FormulaCatalogEntry":
        _require_non_empty(self.formula_id, "formula_id")
        _require_non_empty(self.name, "name")
        _require_non_empty(self.description, "description")
        _require_non_empty_items(self.required_inputs, "required_inputs")
        _require_non_empty_items(self.accepted_sources, "accepted_sources")
        _require_non_empty_items(self.assumptions, "assumptions")
        if len(set(self.required_inputs)) != len(self.required_inputs):
            raise ValueError("required_inputs cannot contain duplicates")
        for field_name in ("unit", "period", "when_not_to_use"):
            value = getattr(self, field_name)
            if value is not None and not value.strip():
                raise ValueError(f"{field_name} cannot be empty")
        return self


class TenantFormulaOverride(BaseModel):
    """Tenant-specific governed override for a formula_catalog entry."""

    cliente_id: str
    formula_id: str
    override_id: str
    overridden_inputs: list[str] | None = None
    assumptions: list[str] | None = None
    unit: str | None = None
    period: str | None = None
    when_not_to_use: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    approved_by: str
    reason: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate(self) -> "TenantFormulaOverride":
        _require_non_empty(self.cliente_id, "cliente_id")
        _require_non_empty(self.formula_id, "formula_id")
        _require_non_empty(self.override_id, "override_id")
        _require_non_empty(self.approved_by, "approved_by")
        _require_non_empty(self.reason, "reason")
        if self.overridden_inputs is not None:
            _require_non_empty_items(self.overridden_inputs, "overridden_inputs")
            if len(set(self.overridden_inputs)) != len(self.overridden_inputs):
                raise ValueError("overridden_inputs cannot contain duplicates")
        if self.assumptions is not None:
            _require_non_empty_items(self.assumptions, "assumptions")
        for field_name in ("unit", "period", "when_not_to_use"):
            value = getattr(self, field_name)
            if value is not None and not value.strip():
                raise ValueError(f"{field_name} cannot be empty")
        return self
