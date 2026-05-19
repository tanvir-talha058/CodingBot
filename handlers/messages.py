"""Handler for plain text messages (free-form coding chat)."""

from __future__ import annotations

import logging

from telegram.constants import ChatAction
from telegram import Update
from telegram.ext import ContextTypes

from ai import copilot
from utils.formatting import split_long_message
from utils.history import history

logger = logging.getLogger(__name__)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Respond to any free-form text message using conversation history."""
    user_id = update.effective_user.id  # type: ignore[union-attr]
    user_text = update.message.text  # type: ignore[union-attr]

    if not user_text:
        return

    # Add user turn to history
    history.add_user(user_id, user_text)

    # Show native typing indicator and a placeholder message
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,  # type: ignore[union-attr]
        action=ChatAction.TYPING,
    )
    thinking_msg = await update.message.reply_text("⏳ Thinking…")  # type: ignore[union-attr]

    # Build conversation and call AI
    messages = history.get(user_id)
    try:
        reply = await copilot.ask(messages)
    except Exception:
        logger.exception("ask failed")
        await thinking_msg.edit_text("❌ Sorry, something went wrong. Please try again.")
        # Roll back only the user turn we just added; preserve the rest of the history
        history.remove_last(user_id)
        return

    # Persist assistant reply in history
    history.add_assistant(user_id, reply)

    # Remove placeholder and send the real reply (split if long)
    await thinking_msg.delete()
    for chunk in split_long_message(reply):
        await update.message.reply_text(chunk)  # type: ignore[union-attr]
