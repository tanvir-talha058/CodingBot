"""CodingBot — Telegram bot entry point.

Run with:
    python bot.py
"""

from __future__ import annotations

import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

import config
from handlers.commands import (
    clear_command,
    code_command,
    debug_command,
    explain_command,
    help_command,
    refactor_command,
    review_command,
    start,
)
from handlers.messages import message_handler

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Build the Telegram Application and start polling."""
    logger.info("Starting CodingBot with model=%s", config.OPENAI_MODEL)

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # ── Command handlers ──────────────────────────────────────────────────
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("code", code_command))
    app.add_handler(CommandHandler("explain", explain_command))
    app.add_handler(CommandHandler("debug", debug_command))
    app.add_handler(CommandHandler("review", review_command))
    app.add_handler(CommandHandler("refactor", refactor_command))
    app.add_handler(CommandHandler("clear", clear_command))

    # ── Free-form text messages ───────────────────────────────────────────
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
