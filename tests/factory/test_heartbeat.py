from factory.control.heartbeat import is_stale, watchdog_state, write_heartbeat


def test_heartbeat_is_not_stale_after_write(tmp_path):
    hb = tmp_path / "heartbeat.json"
    write_heartbeat(hb)
    assert is_stale(hb, max_age_seconds=300) is False
    assert watchdog_state(hb) == "HEALTHY"


def test_missing_heartbeat_escalates(tmp_path):
    assert is_stale(tmp_path / "missing.json") is True
    assert watchdog_state(tmp_path / "missing.json") == "ESCALATED"
