#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml


TOKEN_ENV_KEYS = (
    "TELEGRAM_BOT_TOKEN",
    "HERMES_TELEGRAM_TOKEN",
    "BOT_TOKEN",
    "TELEGRAM_TOKEN",
)


def main() -> int:
    hermes_home = Path(os.environ.get("HERMES_HOME", "~/.hermes")).expanduser()
    config_path = Path(os.environ.get("HERMES_CONFIG_PATH", str(hermes_home / "config.yaml"))).expanduser()
    repo = Path(os.environ.get("SMARTPYME_REPO", ".")).resolve()

    _assert_repo(repo)
    config = _load_config(config_path)
    token = _read_telegram_token(config)
    bot_info = _validate_token(token)

    _stop_local_gateways()
    _remove_gateway_state(hermes_home)

    hermes_bin = shutil.which("hermes")
    if not hermes_bin:
        raise SystemExit("ERROR_HERMES_BINARY_NOT_FOUND")

    env = os.environ.copy()
    for key in TOKEN_ENV_KEYS:
        env.pop(key, None)
    env["HERMES_CONFIG_PATH"] = str(config_path)

    print("HERMES_GATEWAY_CLEAN_LAUNCH_READY", flush=True)
    print(f"repo={repo}", flush=True)
    print(f"config={config_path}", flush=True)
    print(f"telegram_ok=True", flush=True)
    print(f"telegram_username={bot_info.get('username')}", flush=True)
    print(f"telegram_bot_id={bot_info.get('id')}", flush=True)
    print("token_printed=False", flush=True)
    print(f"hermes_bin={hermes_bin}", flush=True)
    print("exec=hermes gateway", flush=True)

    os.chdir(repo)
    os.execvpe(hermes_bin, [hermes_bin, "gateway"], env)
    return 0


def _assert_repo(repo: Path) -> None:
    required = [repo / ".git", repo / "AGENTS.md", repo / "GEMINI.md", repo / "factory"]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("ERROR_NOT_SMARTPYME_REPO: missing " + ", ".join(missing))


def _load_config(config_path: Path) -> dict:
    if not config_path.exists():
        raise SystemExit(f"ERROR_MISSING_HERMES_CONFIG: {config_path}")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8", errors="replace")) or {}
    if not isinstance(config, dict):
        raise SystemExit("ERROR_INVALID_HERMES_CONFIG")
    return config


def _read_telegram_token(config: dict) -> str:
    telegram = config.get("platforms", {}).get("telegram", {})
    token = str(telegram.get("token") or "").strip()
    if not token:
        raise SystemExit("ERROR_MISSING_TELEGRAM_TOKEN_IN_CONFIG")
    if ":" not in token:
        raise SystemExit("ERROR_INVALID_TELEGRAM_TOKEN_FORMAT")
    return token


def _validate_token(token: str) -> dict:
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        payload = urllib.request.urlopen(url, timeout=20).read().decode()
        data = json.loads(payload)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise SystemExit(f"ERROR_TELEGRAM_TOKEN_REJECTED: status={exc.code} body={body}") from exc
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"ERROR_TELEGRAM_TOKEN_CHECK_FAILED: {exc}") from exc

    if data.get("ok") is not True:
        raise SystemExit(f"ERROR_TELEGRAM_TOKEN_NOT_OK: {data}")
    result = data.get("result") or {}
    if not result.get("username"):
        raise SystemExit(f"ERROR_TELEGRAM_GETME_MISSING_USERNAME: {data}")
    return result


def _stop_local_gateways() -> None:
    current_pid = os.getpid()
    try:
        output = subprocess.check_output(["pgrep", "-f", "hermes gateway"], text=True).splitlines()
    except subprocess.CalledProcessError:
        return

    for raw_pid in output:
        try:
            pid = int(raw_pid.strip())
        except ValueError:
            continue
        if pid == current_pid:
            continue
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            continue


def _remove_gateway_state(hermes_home: Path) -> None:
    for relative in ("gateway.lock", "gateway_state.json"):
        path = hermes_home / relative
        try:
            path.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
