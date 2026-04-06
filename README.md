# CodingBot 🤖

A Telegram bot that gives you **GitHub Copilot-style AI coding assistance** right from your phone. Generate code, explain snippets, debug errors, review pull-request-style, and refactor — all via Telegram, even when you're away from your PC.

---

## Features

| Command | Description |
|---|---|
| `/start` | Welcome message & quick overview |
| `/help` | Full command reference |
| `/code <description>` | Generate code from a plain-language description |
| `/explain` | *(reply to code)* Explain what the code does |
| `/debug [error]` | *(reply to code)* Find & fix bugs; optionally include the error message |
| `/review` | *(reply to code)* Code review with quality & security feedback |
| `/refactor [goal]` | *(reply to code)* Refactor for clarity or performance |
| `/clear` | Clear your conversation history |
| *(any message)* | Free-form coding chat with full conversation context |

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | Tested on 3.10, 3.11, 3.12 |
| Telegram account | Needed to create the bot via @BotFather |
| OpenAI API key | [Get one here](https://platform.openai.com/api-keys) |

---

## Quick Start

### 1. Create a Telegram bot

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the prompts.
3. Copy the **API token** BotFather gives you.

### 2. Clone & install

```bash
git clone https://github.com/tanvir-talha058/CodingBot.git
cd CodingBot
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```dotenv
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o          # or gpt-3.5-turbo for lower cost
MAX_HISTORY=10               # conversation turns kept per user
```

### 4. Run the bot

```bash
python bot.py
```

The bot will start polling Telegram for messages. Open the bot in Telegram and send `/start`.

---

## Project Structure

```
CodingBot/
├── bot.py                  # Entry point — builds and starts the Telegram app
├── config.py               # Loads .env configuration
├── requirements.txt        # Python dependencies
├── .env.example            # Template for environment variables
├── ai/
│   ├── __init__.py
│   └── copilot.py          # OpenAI API wrappers (generate, explain, debug, review, refactor)
├── handlers/
│   ├── __init__.py
│   ├── commands.py         # Telegram command handlers
│   └── messages.py         # Free-form message handler (conversational chat)
├── utils/
│   ├── __init__.py
│   ├── formatting.py       # Message splitting / Markdown escaping helpers
│   └── history.py          # Per-user conversation history manager
└── tests/
    ├── test_formatting.py
    └── test_history.py
```

---

## Running Tests

```bash
pip install pytest
TELEGRAM_BOT_TOKEN=dummy OPENAI_API_KEY=dummy python -m pytest tests/ -v
```

---

## Usage Examples

### Generate code
```
/code a Python function that checks if a string is a palindrome
```

### Explain code
*First send the code snippet as a message, then reply to it with:*
```
/explain
```

### Debug with error
*Reply to your code message with:*
```
/debug TypeError: 'NoneType' object is not subscriptable
```

### Refactor with a goal
*Reply to your code message with:*
```
/refactor improve readability and add type hints
```

### Free-form chat
```
How do I implement a singleton pattern in Python?
```

---

## Configuration Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ | — | Token from @BotFather |
| `OPENAI_API_KEY` | ✅ | — | OpenAI API key |
| `OPENAI_MODEL` | ❌ | `gpt-4o` | OpenAI model to use |
| `MAX_HISTORY` | ❌ | `10` | Number of conversation turns kept per user |

---

## License

MIT
