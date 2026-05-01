from __future__ import annotations

import hashlib
import re
from typing import Any

from app.contracts.evidence_contract import ExtractedFactCandidate
from app.repositories.fact_repository import FactRepository


class FactExtractionService:
    AMOUNT_PATTERN = re.compile(r"(?<!\w)(?:\$\s*\d+(?:[.,]\d{1,2})?|\d+(?:[.,]\d{2}))(?!\w)")
    DATE_PATTERN = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")
    CUIT_PATTERN = re.compile(r"\b\d{2}-\d{8}-\d\b")

    def __init__(self, repository: FactRepository) -> None:
        self.repository = repository

    def extract_from_evidence(
        self,
        cliente_id: str,
        evidence_id: str,
        text: str,
        *,
        job_id: str | None = None,
        plan_id: str | None = None,
    ) -> dict[str, Any]:
        facts = self._extract_facts(
            cliente_id=cliente_id,
            evidence_id=evidence_id,
            text=text,
            job_id=job_id,
            plan_id=plan_id,
        )
        self.repository.save_batch(facts)
        return {
            "status": "EXTRACTED",
            "evidence_id": evidence_id,
            "facts_count": len(facts),
            "fact_ids": [fact.fact_candidate_id for fact in facts],
        }

    def _extract_facts(
        self,
        *,
        cliente_id: str,
        evidence_id: str,
        text: str,
        job_id: str | None,
        plan_id: str | None,
    ) -> list[ExtractedFactCandidate]:
        facts: list[ExtractedFactCandidate] = []
        blocked_spans = [
            match.span()
            for pattern in (self.DATE_PATTERN, self.CUIT_PATTERN)
            for match in pattern.finditer(text)
        ]
        facts.extend(
            self._build_facts(
                cliente_id=cliente_id,
                evidence_id=evidence_id,
                job_id=job_id,
                plan_id=plan_id,
                fact_type="amount",
                values=[
                    match.group().strip().replace("$", "").strip()
                    for match in self.AMOUNT_PATTERN.finditer(text)
                    if not _overlaps_any(match.span(), blocked_spans)
                ],
            )
        )
        facts.extend(
            self._build_facts(
                cliente_id=cliente_id,
                evidence_id=evidence_id,
                job_id=job_id,
                plan_id=plan_id,
                fact_type="date",
                values=[match.group() for match in self.DATE_PATTERN.finditer(text)],
            )
        )
        facts.extend(
            self._build_facts(
                cliente_id=cliente_id,
                evidence_id=evidence_id,
                job_id=job_id,
                plan_id=plan_id,
                fact_type="cuit",
                values=[match.group() for match in self.CUIT_PATTERN.finditer(text)],
            )
        )
        return facts

    def _build_facts(
        self,
        *,
        cliente_id: str,
        evidence_id: str,
        job_id: str | None,
        plan_id: str | None,
        fact_type: str,
        values: list[str],
    ) -> list[ExtractedFactCandidate]:
        facts: list[ExtractedFactCandidate] = []
        for index, value in enumerate(values):
            data = {"fact_type": fact_type, "value": value}
            facts.append(
                ExtractedFactCandidate(
                    cliente_id=cliente_id,
                    fact_candidate_id=_build_fact_id(evidence_id, fact_type, value, index),
                    evidence_id=evidence_id,
                    job_id=job_id,
                    plan_id=plan_id,
                    schema_name=f"simple_{fact_type}",
                    data=data,
                    confidence=1.0,
                    extraction_method="deterministic_regex",
                    validation_status="pending_validation",
                    errors=[],
                )
            )
        return facts


def _build_fact_id(evidence_id: str, fact_type: str, value: str, index: int) -> str:
    digest = hashlib.sha256(f"{evidence_id}:{fact_type}:{value}:{index}".encode()).hexdigest()
    return f"fact_{digest[:16]}"


def _overlaps_any(span: tuple[int, int], blocked_spans: list[tuple[int, int]]) -> bool:
    start, end = span
    return any(start < blocked_end and end > blocked_start for blocked_start, blocked_end in blocked_spans)
