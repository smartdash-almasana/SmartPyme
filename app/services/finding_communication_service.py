from __future__ import annotations

from app.contracts.communication_contract import FindingMessage, build_message_id
from app.services.findings_service import Finding

# Severity labels in Spanish for human-facing messages.
_SEVERITY_LABEL: dict[str, str] = {
    "CRITICO": "⚠️ CRÍTICO",
    "ALTO":    "🔴 ALTO",
    "MEDIO":   "🟡 MEDIO",
    "BAJO":    "🟢 BAJO",
    "INFO":    "ℹ️ INFO",
}


class FindingCommunicationService:
    """
    Converts Finding objects into human-readable FindingMessage objects.
    Does NOT send messages. Does NOT call external services.
    """

    def build_message(self, finding: Finding, channel: str = "internal") -> FindingMessage:
        severity_label = _SEVERITY_LABEL.get(finding.severity, finding.severity)

        title = (
            f"[{severity_label}] Diferencia en {finding.entity_type.upper()} "
            f"— métrica: {finding.metric}"
        )

        diff_sign = "+" if finding.difference > 0 else ""
        body = (
            f"Se detectó una diferencia en la métrica '{finding.metric}' "
            f"entre las entidades '{finding.entity_id_a}' y '{finding.entity_id_b}' "
            f"(tipo: {finding.entity_type}).\n"
            f"\n"
            f"  • Valor A: {finding.source_a_value}\n"
            f"  • Valor B: {finding.source_b_value}\n"
            f"  • Diferencia: {diff_sign}{finding.difference:.2f} "
            f"({diff_sign}{finding.difference_pct:.1f}%)\n"
            f"\n"
            f"Severidad: {severity_label}"
        )

        return FindingMessage(
            message_id=build_message_id(finding.finding_id, channel),
            finding_id=finding.finding_id,
            channel=channel,
            title=title,
            body=body,
            action_text=finding.suggested_action,
            severity=finding.severity,
            traceable_origin=finding.traceable_origin,
        )

    def build_messages(
        self, findings: list[Finding], channel: str = "internal"
    ) -> list[FindingMessage]:
        return [self.build_message(f, channel) for f in findings]
