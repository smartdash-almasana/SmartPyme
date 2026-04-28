from factory.control.circuit_breaker import CircuitBreaker
from factory.control.heartbeat import is_stale, write_heartbeat
from factory.control.telegram_handler import create_callback_token, mark_update_processed, resolve_callback_token


def test_factory_dry_run_cycle(tmp_path):
    db = tmp_path / "telegram.db"
    hb = tmp_path / "heartbeat.json"

    assert mark_update_processed(1, "/estado", db_path=db) is True
    assert mark_update_processed(1, "/estado", db_path=db) is False

    token = create_callback_token("cycle-001", "APPROVE", db_path=db)
    assert len(token.encode("utf-8")) <= 64
    assert resolve_callback_token(token, db_path=db)["action"] == "APPROVE"

    write_heartbeat(hb)
    assert is_stale(hb, max_age_seconds=300) is False

    breaker = CircuitBreaker(max_failures_per_hour=1)
    assert breaker.record_failure() is False
    assert breaker.record_failure() is True
    assert breaker.is_open() is True
