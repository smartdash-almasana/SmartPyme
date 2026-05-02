from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.catalogs.operational_conditions_catalog import OPERATIONAL_CONDITIONS_CATALOG


@dataclass(frozen=True, slots=True)
class CurationResult:
    status: str
    errors: list[str] = field(default_factory=list)
    cleaned_payload: dict[str, Any] = field(default_factory=dict)


class DataCurationService:
    """Service for data hygiene and technical validation before business logic.

    Rules:
    - RELEVANCE: Filter keys not in conditions catalog.
    - STRUCTURE: Basic type conversion (str -> float).
    - DOMAIN: Range validation (>0) and format (YYYY-MM).
    - PRESENCE: No null or empty strings.
    """

    def curate_input(
        self,
        skill_id: str,
        variables: dict[str, Any],
        evidence: list[str],
        objective: str | None,
    ) -> CurationResult:
        conditions = OPERATIONAL_CONDITIONS_CATALOG.get(skill_id)
        if not conditions:
            return CurationResult(status="CURATION_INVALID", errors=["UNKNOWN_SKILL"])

        errors = []
        cleaned_vars = {}
        
        # 1. Relevance & Structure & Domain for Variables
        for key, value in variables.items():
            # RELEVANCE: Filter out keys not in the catalog
            if key not in conditions.required_variables:
                continue

            # PRESENCE: No null
            if value is None:
                errors.append(f"FIELD_NULL: {key}")
                continue

            # STRUCTURE & DOMAIN:
            try:
                # Basic conversion for numerical fields (guessed by name or type)
                if isinstance(value, str) and re.match(r"^-?\d+(\.\d+)?$", value.strip()):
                    value = float(value.strip())

                # DOMAIN: Periodo format YYYY-MM
                if key == "periodo":
                    if not isinstance(value, str) or not re.match(r"^\d{4}-\d{2}$", value.strip()):
                        errors.append(f"INVALID_FORMAT: {key} must be YYYY-MM")
                        continue
                    value = value.strip()
                
                # DOMAIN: Numerical values should be non-negative (simple rule for SME OS)
                if isinstance(value, (int, float)):
                    if value < 0:
                        errors.append(f"INVALID_RANGE: {key} must be >= 0")
                        continue
                
                # PRESENCE: Empty string
                if isinstance(value, str) and not value.strip():
                    errors.append(f"FIELD_EMPTY: {key}")
                    continue

                cleaned_vars[key] = value

            except Exception:
                errors.append(f"STRUCTURE_ERROR: {key}")

        # 2. Evidence filtering
        cleaned_ev = [e for e in evidence if e in conditions.required_evidence]

        # 3. Objective sanitization
        cleaned_obj = objective.strip() if objective else ""

        # 4. Result determination
        if errors:
            return CurationResult(status="CURATION_INVALID", errors=errors)

        # Check if we have everything (INSUFFICIENT if missing required)
        # Note: Conditions service also checks this, but Curator handles "empty" vs "missing"
        missing_required_vars = [v for v in conditions.required_variables if v not in cleaned_vars]
        missing_required_ev = [e for e in conditions.required_evidence if e not in cleaned_ev]

        if missing_required_vars or missing_required_ev:
            return CurationResult(
                status="CURATION_INSUFFICIENT",
                cleaned_payload={
                    "variables": cleaned_vars,
                    "evidence": cleaned_ev,
                    "objective": cleaned_obj,
                }
            )

        return CurationResult(
            status="CURATION_OK",
            cleaned_payload={
                "variables": cleaned_vars,
                "evidence": cleaned_ev,
                "objective": cleaned_obj,
            }
        )
