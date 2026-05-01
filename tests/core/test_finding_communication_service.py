import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.contracts.communication_contract import FindingMessage
from app.services.finding_communication_service import FindingCommunicationService
from app.services.findings_service import Finding


def _finding(
    finding_id: str = "finding-1",
    *,
    entity_id_a: str = "ent-a",
    entity_id_b: str = "ent-b",
    entity_type: str = "cuit",
    metric: str = "price",
    source_a_value: Any = 1500.25,
    source_b_value: Any = 1800.00,
    difference: float = 299.75,
    difference_pct: float = 19.98,
    severity: str = "ALTO",
    suggested_action: str = "Revisión recomendada",
    traceable_origin: dict | None = None,
) -> Finding:
    return Finding(
        finding_id=finding_id,
        entity_id_a=entity_id_a,
        entity_id_b=entity_id_b,
        entity_type=entity_type,
        metric=metric,
        source_a_value=source_a_value,
        source_b_value=source_b_value,
        difference=difference,
        difference_pct=difference_pct,
        severity=severity,
        suggested_action=suggested_action,
        traceable_origin=traceable_origin or {},
    )


def test_build_message_returns_finding_message():
    service = FindingCommunicationService()
    msg = service.build_message(_finding())

    assert isinstance(msg, FindingMessage)


def test_build_message_default_channel_is_internal():
    service = FindingCommunicationService()
    msg = service.build_message(_finding())

    assert msg.channel == "internal"


def test_build_message_preserves_finding_id():
    service = FindingCommunicationService()
    msg = service.build_message(_finding("f-xyz"))

    assert msg.finding_id == "f-xyz"


def test_build_message_title_contains_entity_type_and_metric():
    service = FindingCommunicationService()
    msg = service.build_message(_finding(entity_type="invoice", metric="amount"))

    assert "INVOICE" in msg.title
    assert "amount" in msg.title


def test_build_message_body_contains_entity_ids():
    service = FindingCommunicationService()
    msg = service.build_message(_finding(entity_id_a="ent-001", entity_id_b="ent-002"))

    assert "ent-001" in msg.body
    assert "ent-002" in msg.body


def test_build_message_body_contains_both_values():
    service = FindingCommunicationService()
    msg = service.build_message(_finding(source_a_value=1500.25, source_b_value=1800.00))

    assert "1500.25" in msg.body
    assert "1800.0" in msg.body


def test_build_message_body_contains_difference():
    service = FindingCommunicationService()
    # difference_pct=20.0 → formatted as "20.0%" (:.1f rounds 19.98 → 20.0)
    msg = service.build_message(_finding(difference=299.75, difference_pct=20.0))

    assert "299.75" in msg.body
    assert "20.0" in msg.body


def test_build_message_severity_matches_finding():
    service = FindingCommunicationService()
    for severity in ("CRITICO", "ALTO", "MEDIO", "BAJO", "INFO"):
        msg = service.build_message(_finding(severity=severity))
        assert msg.severity == severity


def test_build_message_action_text_matches_suggested_action():
    service = FindingCommunicationService()
    msg = service.build_message(_finding(suggested_action="Revisión inmediata requerida"))

    assert msg.action_text == "Revisión inmediata requerida"


def test_build_message_preserves_traceable_origin():
    origin = {"comparison_result": {"entity_id_a": "a", "value": 42}}
    service = FindingCommunicationService()
    msg = service.build_message(_finding(traceable_origin=origin))

    assert msg.traceable_origin == origin


def test_build_message_message_id_is_deterministic():
    service = FindingCommunicationService()
    f = _finding("f-stable")
    msg1 = service.build_message(f, channel="internal")
    msg2 = service.build_message(f, channel="internal")

    assert msg1.message_id == msg2.message_id


def test_build_message_message_id_differs_by_channel():
    service = FindingCommunicationService()
    f = _finding("f-stable")
    msg_internal = service.build_message(f, channel="internal")
    msg_telegram = service.build_message(f, channel="telegram")

    assert msg_internal.message_id != msg_telegram.message_id


def test_build_messages_returns_one_per_finding():
    service = FindingCommunicationService()
    findings = [_finding("f-1"), _finding("f-2"), _finding("f-3")]
    messages = service.build_messages(findings)

    assert len(messages) == 3
    ids = {m.finding_id for m in messages}
    assert ids == {"f-1", "f-2", "f-3"}


def test_build_messages_empty_input_returns_empty_list():
    service = FindingCommunicationService()
    assert service.build_messages([]) == []


def test_build_messages_custom_channel_propagates():
    service = FindingCommunicationService()
    messages = service.build_messages([_finding("f-1"), _finding("f-2")], channel="whatsapp")

    assert all(m.channel == "whatsapp" for m in messages)
