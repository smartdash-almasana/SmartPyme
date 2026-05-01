import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.contracts.communication_contract import FindingMessage, build_message_id


def test_finding_message_is_dataclass():
    from dataclasses import fields
    field_names = {f.name for f in fields(FindingMessage)}
    required = {"message_id", "finding_id", "channel", "title", "body",
                "action_text", "severity", "traceable_origin"}
    assert required.issubset(field_names)


def test_finding_message_is_frozen():
    msg = FindingMessage(
        message_id="msg-1",
        finding_id="f-1",
        channel="internal",
        title="Test title",
        body="Test body",
        action_text="Do something",
        severity="ALTO",
        traceable_origin={},
    )
    try:
        object.__setattr__(msg, "title", "mutated")
        raise AssertionError("Should have raised FrozenInstanceError")
    except Exception:
        pass  # frozen — expected


def test_build_message_id_is_deterministic():
    id1 = build_message_id("finding-1", "internal")
    id2 = build_message_id("finding-1", "internal")
    assert id1 == id2
    assert id1.startswith("msg_")


def test_build_message_id_differs_by_finding():
    id1 = build_message_id("finding-1", "internal")
    id2 = build_message_id("finding-2", "internal")
    assert id1 != id2


def test_build_message_id_differs_by_channel():
    id1 = build_message_id("finding-1", "internal")
    id2 = build_message_id("finding-1", "telegram")
    assert id1 != id2


def test_finding_message_traceable_origin_defaults_to_empty_dict():
    msg = FindingMessage(
        message_id="msg-1",
        finding_id="f-1",
        channel="internal",
        title="T",
        body="B",
        action_text="A",
        severity="INFO",
    )
    assert msg.traceable_origin == {}
