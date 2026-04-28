from factory.control.circuit_breaker import CircuitBreaker


def test_circuit_breaker_trips_after_threshold():
    breaker = CircuitBreaker(max_failures_per_hour=1)
    assert breaker.record_failure() is False
    assert breaker.record_failure() is True
    assert breaker.is_open() is True
    assert breaker.snapshot()["is_open"] is True


def test_circuit_breaker_reset():
    breaker = CircuitBreaker(max_failures_per_hour=0)
    breaker.record_failure()
    assert breaker.is_open() is True
    breaker.reset()
    assert breaker.is_open() is False
