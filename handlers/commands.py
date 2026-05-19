"""Telegram command handlers (/start, /help, /code, /explain, /debug, /review, /refactor, /clear)."""

from __future__ import annotations

import logging

from telegram import Message, Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from ai import copilot
from utils.formatting import split_long_message
from utils.history import history

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _send(update: Update, text: str, parse_mode: str | None = None) -> None:
    """Send a (possibly long) message, splitting if needed."""
    chunks = split_long_message(text)
    for chunk in chunks:
        await update.message.reply_text(chunk, parse_mode=parse_mode)  # type: ignore[union-attr]


async def _thinking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
    """Send a typing action and a 'thinking…' placeholder.

    Returns the placeholder message so the caller can delete it on success
    or edit it into an error message on failure.
    """
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,  # type: ignore[union-attr]
        action=ChatAction.TYPING,
    )
    return await update.message.reply_text("⏳ Thinking…")  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# /start
# ---------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # noqa: ARG001
    """Welcome message."""
    user = update.effective_user
    name = user.first_name if user else "there"
    await _send(
        update,
        f"👋 Hi <b>{name}</b>! I'm <b>CodingBot</b> — your AI coding assistant.\n\n"
        "I can help you:\n"
        "• 🧑‍💻 <b>/code</b> — Generate code from a description\n"
        "• 📖 <b>/explain</b> — Explain code you paste\n"
        "• 🐛 <b>/debug</b> — Find & fix bugs in your code\n"
        "• 🔍 <b>/review</b> — Review code for quality &amp; security\n"
        "• ♻️ <b>/refactor</b> — Refactor code for clarity/performance\n"
        "• 💬 Chat freely — just send any message!\n\n"
        "Type /help to see all commands, or just ask me anything!",
        parse_mode=ParseMode.HTML,
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

_Tip: paste code directly in your message and I'll detect and respond to it\\._
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
        await _send(
            update,
            "ℹ️ <b>Usage:</b> /code &lt;description&gt;\n"
            "<b>Example:</b> <code>/code a Python binary search function</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    full_text = " ".join(args)

    # Allow user to hint language with "lang:python" at end
    language = ""
    if "lang:" in full_text.lower():
        parts = full_text.rsplit("lang:", 1)
        full_text = parts[0].strip()
        language = parts[1].strip()

    thinking_msg = await _thinking(update, context)
    try:
        reply = await copilot.generate_code(full_text, language)
    except Exception:
        logger.exception("generate_code failed")
        await thinking_msg.edit_text("❌ Sorry, something went wrong. Please try again.")
        return
    await thinking_msg.delete()
    await _send(update, reply)


# ---------------------------------------------------------------------------
# /explain
# ---------------------------------------------------------------------------

async def explain_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explain the code in the replied-to message."""
    code = _extract_replied_code(update)
    if code is None:
        await _send(
            update,
            "ℹ️ Please <b>reply</b> to a message containing code, then use /explain.",
            parse_mode=ParseMode.HTML,
        )
        return
    thinking_msg = await _thinking(update, context)
    try:
        reply = await copilot.explain_code(code)
    except Exception:
        logger.exception("explain_code failed")
        await thinking_msg.edit_text("❌ Sorry, something went wrong. Please try again.")
        return
    await thinking_msg.delete()
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
        await _send(
            update,
            "ℹ️ Please <b>reply</b> to a message containing code, then use /debug [error message].",
            parse_mode=ParseMode.HTML,
        )
        return
    error = " ".join(context.args) if context.args else ""
    thinking_msg = await _thinking(update, context)
    try:
        reply = await copilot.debug_code(code, error)
    except Exception:
        logger.exception("debug_code failed")
        await thinking_msg.edit_text("❌ Sorry, something went wrong. Please try again.")
        return
    await thinking_msg.delete()
    await _send(update, reply)


# ---------------------------------------------------------------------------
# /review
# ---------------------------------------------------------------------------

async def review_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Review the code in the replied-to message."""
    code = _extract_replied_code(update)
    if code is None:
        await _send(
            update,
            "ℹ️ Please <b>reply</b> to a message containing code, then use /review.",
            parse_mode=ParseMode.HTML,
        )
        return
    thinking_msg = await _thinking(update, context)
    try:
        reply = await copilot.review_code(code)
    except Exception:
        logger.exception("review_code failed")
        await thinking_msg.edit_text("❌ Sorry, something went wrong. Please try again.")
        return
    await thinking_msg.delete()
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
        await _send(
            update,
            "ℹ️ Please <b>reply</b> to a message containing code, then use /refactor [goal].",
            parse_mode=ParseMode.HTML,
        )
        return
    goal = " ".join(context.args) if context.args else ""
    thinking_msg = await _thinking(update, context)
    try:
        reply = await copilot.refactor_code(code, goal)
    except Exception:
        logger.exception("refactor_code failed")
        await thinking_msg.edit_text("❌ Sorry, something went wrong. Please try again.")
        return
    await thinking_msg.delete()
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
