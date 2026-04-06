"""Telegram command handlers (/start, /help, /code, /explain, /debug, /review, /refactor, /clear)."""

from __future__ import annotations

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ai import copilot
from utils.formatting import split_long_message
from utils.history import history

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _send(update: Update, text: str) -> None:
    """Send a (possibly long) message, splitting if needed."""
    chunks = split_long_message(text)
    for chunk in chunks:
        await update.message.reply_text(chunk)  # type: ignore[union-attr]


async def _thinking(update: Update) -> None:
    """Send a 'thinking…' placeholder while waiting for the AI."""
    await update.message.reply_text("⏳ Thinking…")  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# /start
# ---------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # noqa: ARG001
    """Welcome message."""
    user = update.effective_user
    name = user.first_name if user else "there"
    await _send(
        update,
        f"👋 Hi {name}! I'm *CodingBot* — your AI coding assistant powered by GitHub Copilot.\n\n"
        "I can help you:\n"
        "• 🧑‍💻 Generate code from a description\n"
        "• 📖 Explain code you paste\n"
        "• 🐛 Debug errors in your code\n"
        "• 🔍 Review code for quality & security\n"
        "• ♻️ Refactor code for clarity/performance\n"
        "• 💬 Chat freely about any coding topic\n\n"
        "Type /help to see all commands, or just ask me anything!",
    )


# ---------------------------------------------------------------------------
# /help
# ---------------------------------------------------------------------------

HELP_TEXT = """*CodingBot — Command Reference*

*General*
/start — Welcome message
/help — Show this help
/clear — Clear your conversation history

*Code Generation*
/code \\<description\\> — Generate code from a description
Example: `/code a Python function to sort a list of dicts by key`

*Code Analysis (reply to a code message)*
/explain — Explain what the replied-to code does
/debug \\[error message\\] — Find & fix bugs (optional: include the error)
/review — Perform a code review
/refactor \\[goal\\] — Refactor the code (optional: specify goal)

*Free-form chat*
Just send any message and I'll answer as your coding assistant!

_Tip: paste code directly in your message and I'll detect and respond to it._
"""


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # noqa: ARG001
    """Show help text."""
    await update.message.reply_text(  # type: ignore[union-attr]
        HELP_TEXT, parse_mode=ParseMode.MARKDOWN_V2
    )


# ---------------------------------------------------------------------------
# /code
# ---------------------------------------------------------------------------

async def code_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate code from a plain-language description.

    Usage: /code <description> [lang:<language>]
    Example: /code a REST API endpoint in Python using Flask
    """
    args = context.args or []
    if not args:
        await _send(update, "Usage: /code <description>\nExample: /code a Python binary search function")
        return

    full_text = " ".join(args)

    # Allow user to hint language with "lang:python" at end
    language = ""
    if "lang:" in full_text.lower():
        parts = full_text.rsplit("lang:", 1)
        full_text = parts[0].strip()
        language = parts[1].strip()

    await _thinking(update)
    reply = await copilot.generate_code(full_text, language)
    await _send(update, reply)


# ---------------------------------------------------------------------------
# /explain
# ---------------------------------------------------------------------------

async def explain_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # noqa: ARG001
    """Explain the code in the replied-to message."""
    code = _extract_replied_code(update)
    if code is None:
        await _send(update, "Please *reply* to a message containing code, then use /explain.")
        return
    await _thinking(update)
    reply = await copilot.explain_code(code)
    await _send(update, reply)


# ---------------------------------------------------------------------------
# /debug
# ---------------------------------------------------------------------------

async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Debug the code in the replied-to message.

    Usage: Reply to a code message with /debug [optional error text]
    """
    code = _extract_replied_code(update)
    if code is None:
        await _send(update, "Please *reply* to a message containing code, then use /debug [error message].")
        return
    error = " ".join(context.args) if context.args else ""
    await _thinking(update)
    reply = await copilot.debug_code(code, error)
    await _send(update, reply)


# ---------------------------------------------------------------------------
# /review
# ---------------------------------------------------------------------------

async def review_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # noqa: ARG001
    """Review the code in the replied-to message."""
    code = _extract_replied_code(update)
    if code is None:
        await _send(update, "Please *reply* to a message containing code, then use /review.")
        return
    await _thinking(update)
    reply = await copilot.review_code(code)
    await _send(update, reply)


# ---------------------------------------------------------------------------
# /refactor
# ---------------------------------------------------------------------------

async def refactor_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Refactor the code in the replied-to message.

    Usage: Reply to code with /refactor [optional goal, e.g. "improve performance"]
    """
    code = _extract_replied_code(update)
    if code is None:
        await _send(update, "Please *reply* to a message containing code, then use /refactor [goal].")
        return
    goal = " ".join(context.args) if context.args else ""
    await _thinking(update)
    reply = await copilot.refactor_code(code, goal)
    await _send(update, reply)


# ---------------------------------------------------------------------------
# /clear
# ---------------------------------------------------------------------------

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # noqa: ARG001
    """Clear the user's conversation history."""
    user_id = update.effective_user.id  # type: ignore[union-attr]
    history.clear(user_id)
    await _send(update, "🗑️ Conversation history cleared!")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _extract_replied_code(update: Update) -> str | None:
    """Return the text of the message the user replied to, or None."""
    msg = update.message  # type: ignore[union-attr]
    if msg and msg.reply_to_message and msg.reply_to_message.text:
        return msg.reply_to_message.text
    return None
