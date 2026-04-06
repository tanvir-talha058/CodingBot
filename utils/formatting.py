"""Text formatting utilities for Telegram messages."""

from __future__ import annotations

# Telegram MarkdownV2 special characters that must be escaped
_MDV2_SPECIAL = r"\_*[]()~`>#+-=|{}.!"


def escape_mdv2(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2 (outside code blocks)."""
    for ch in _MDV2_SPECIAL:
        text = text.replace(ch, f"\\{ch}")
    return text


def truncate(text: str, max_length: int = 4000) -> str:
    """Truncate text to fit within Telegram's message size limit."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def split_long_message(text: str, max_length: int = 4000) -> list[str]:
    """Split a long message into multiple chunks that respect code blocks.

    Tries to split at newlines rather than in the middle of a line, and avoids
    splitting inside a fenced code block.
    """
    if len(text) <= max_length:
        return [text]

    chunks: list[str] = []
    current = ""
    inside_code = False

    for line in text.splitlines(keepends=True):
        # Track code fence state
        stripped = line.strip()
        if stripped.startswith("```"):
            inside_code = not inside_code

        if len(current) + len(line) > max_length and not inside_code:
            if current:
                chunks.append(current)
            current = line
        else:
            current += line

    if current:
        chunks.append(current)

    return chunks or [text]
