"""Handler for plain text messages (free-form coding chat)."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from ai import copilot
from utils.formatting import split_long_message
from utils.history import history


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # noqa: ARG001
    """Respond to any free-form text message using conversation history."""
    user_id = update.effective_user.id  # type: ignore[union-attr]
    user_text = update.message.text  # type: ignore[union-attr]

    if not user_text:
        return

    # Add user turn to history
    history.add_user(user_id, user_text)

    # Send typing indicator
    await update.message.reply_text("⏳ Thinking…")  # type: ignore[union-attr]

    # Build conversation and call AI
    messages = history.get(user_id)
    reply = await copilot.ask(messages)

    # Persist assistant reply in history
    history.add_assistant(user_id, reply)

    # Send reply (split if long)
    for chunk in split_long_message(reply):
        await update.message.reply_text(chunk)  # type: ignore[union-attr]
