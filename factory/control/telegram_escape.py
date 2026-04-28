"""Telegram MarkdownV2 escaping for SmartPyme Factory."""
from __future__ import annotations

import re

_ESCAPE_CHARS = r"_*[]()~`>#+-=|{}. !"
_PATTERN = re.compile(f"([{re.escape(_ESCAPE_CHARS)}])")


def escape_markdown_v2(text: str) -> str:
    """Escape Telegram MarkdownV2 reserved characters."""
    return _PATTERN.sub(r"\\\1", str(text))
