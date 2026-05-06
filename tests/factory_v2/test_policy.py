"""Tests para CommandPolicyV2."""

import pytest
from factory_v2.policy import CommandPolicyV2

@pytest.fixture
def policy() -> CommandPolicyV2:
    """Proporciona una instancia fresca de la política para cada test."""
    return CommandPolicyV2()

def test_allowlist_commands_are_allowed(policy: CommandPolicyV2):
    """Verifica que los comandos básicos en la allowlist son permitidos."""
    allowed, reason = policy.evaluate("ls -la /tmp")
    assert allowed is True
    assert "está permitido" in reason
    assert "ls" in reason

    allowed, _ = policy.evaluate("python --version")
    assert allowed is True

    allowed, _ = policy.evaluate("pytest tests/")
    assert allowed is True

def test_blocklist_commands_are_blocked(policy: CommandPolicyV2):
    """Verifica que los comandos en la blocklist son bloqueados explícitamente."""
    allowed, reason = policy.evaluate("rm -rf /")
    assert allowed is False
    assert "está en la blocklist" in reason
    assert "rm" in reason

    allowed, reason = policy.evaluate("git status")
    assert allowed is False
    assert "está en la blocklist" in reason

    allowed, reason = policy.evaluate("curl https://example.com")
    assert allowed is False
    assert "está en la blocklist" in reason

def test_unknown_commands_are_blocked_by_default(policy: CommandPolicyV2):
    """Verifica que un comando no listado es bloqueado por defecto (fail-closed)."""
    allowed, reason = policy.evaluate("npm install")
    assert allowed is False
    assert "no está en la allowlist" in reason
    assert "npm" in reason

    allowed, reason = policy.evaluate("unoconv -f pdf my_doc.docx")
    assert allowed is False
    assert "no está en la allowlist" in reason

def test_empty_or_whitespace_commands_are_blocked(policy: CommandPolicyV2):
    """Verifica que comandos vacíos o solo con espacios son bloqueados."""
    allowed, reason = policy.evaluate("")
    assert allowed is False
    assert "vacío" in reason

    allowed, reason = policy.evaluate("    ")
    assert allowed is False
    assert "vacío" in reason

def test_command_is_trimmed(policy: CommandPolicyV2):
    """Verifica que espacios al inicio o final del comando son ignorados."""
    allowed, _ = policy.evaluate("  ls -l  ")
    assert allowed is True

    allowed, _ = policy.evaluate("  rm -f file  ")
    assert allowed is False

def test_reasons_are_clear(policy: CommandPolicyV2):
    """Verifica que los mensajes de razón son informativos."""
    _, reason_allowed = policy.evaluate("echo 'hello world'")
    assert "Comando 'echo' está en la allowlist y está permitido." == reason_allowed

    _, reason_blocked = policy.evaluate("sudo reboot")
    assert "Comando 'sudo' está en la blocklist y está bloqueado." == reason_blocked

    _, reason_default_block = policy.evaluate("htop")
    assert "Comando 'htop' no está en la allowlist y está bloqueado por defecto." == reason_default_block
