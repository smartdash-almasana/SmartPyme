"""Tests para CodePolicyV2."""

from factory_v2.code_policy import CodePolicyV2


def test_allows_simple_python_code() -> None:
    policy = CodePolicyV2()

    allowed, reasons = policy.evaluate(
        code="def add(a, b):\n    return a + b\n",
        test_code="assert add(1, 2) == 3\n",
    )

    assert allowed is True
    assert reasons == []


def test_blocks_empty_code_fail_closed() -> None:
    policy = CodePolicyV2()

    allowed, reasons = policy.evaluate(code="   ", test_code="assert True")

    assert allowed is False
    assert reasons == ["CODE_EMPTY_BLOCKED"]


def test_blocks_os_import() -> None:
    policy = CodePolicyV2()

    allowed, reasons = policy.evaluate(code="import os\n", test_code="")

    assert allowed is False
    assert "IMPORT_OS_BLOCKED" in reasons


def test_blocks_subprocess_import() -> None:
    policy = CodePolicyV2()

    allowed, reasons = policy.evaluate(code="from subprocess import run\n", test_code="")

    assert allowed is False
    assert "SUBPROCESS_BLOCKED" in reasons


def test_blocks_network_related_patterns() -> None:
    policy = CodePolicyV2()

    allowed, reasons = policy.evaluate(
        code="def fetch():\n    return requests.get('https://example.com')\n",
        test_code="",
    )

    assert allowed is False
    assert "REQUESTS_BLOCKED" in reasons

    allowed, reasons = policy.evaluate(
        code="def make_socket(socket_factory):\n    return socket_factory()\n",
        test_code="",
    )

    assert allowed is False
    assert "SOCKET_BLOCKED" in reasons


def test_blocks_file_io_patterns() -> None:
    policy = CodePolicyV2()

    allowed, reasons = policy.evaluate(
        code="def read_file():\n    return open('x.txt').read()\n",
        test_code="",
    )

    assert allowed is False
    assert "OPEN_BLOCKED" in reasons

    allowed, reasons = policy.evaluate(
        code="import pathlib\ndef p():\n    return pathlib.Path('x')\n",
        test_code="",
    )

    assert allowed is False
    assert "PATHLIB_PATH_BLOCKED" in reasons


def test_blocks_dynamic_execution() -> None:
    policy = CodePolicyV2()

    allowed, reasons = policy.evaluate(
        code="def run(expr):\n    return eval(expr)\n",
        test_code="exec('x = 1')\n",
    )

    assert allowed is False
    assert "EVAL_BLOCKED" in reasons
    assert "EXEC_BLOCKED" in reasons


def test_blocks_dynamic_import() -> None:
    policy = CodePolicyV2()

    allowed, reasons = policy.evaluate(
        code="module = __import__('os')\n",
        test_code="",
    )

    assert allowed is False
    assert "DYNAMIC_IMPORT_BLOCKED" in reasons


def test_test_code_is_also_evaluated() -> None:
    policy = CodePolicyV2()

    allowed, reasons = policy.evaluate(
        code="def ok():\n    return 1\n",
        test_code="import os\nassert ok() == 1\n",
    )

    assert allowed is False
    assert "IMPORT_OS_BLOCKED" in reasons
