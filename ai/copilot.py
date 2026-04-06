"""AI Copilot integration using OpenAI API."""

from __future__ import annotations

from openai import AsyncOpenAI

import config

_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "You are CodingBot, an expert AI coding assistant similar to GitHub Copilot. "
    "You help developers write, debug, explain, review, and refactor code. "
    "When providing code examples, always wrap them in triple-backtick fenced code blocks "
    "with the appropriate language tag (e.g. ```python ... ```). "
    "Be concise and practical. If asked a general coding question, answer it directly. "
    "If asked to generate code, produce clean, well-commented, production-ready code."
)


async def ask(
    messages: list[dict[str, str]],
    system_prompt: str = SYSTEM_PROMPT,
) -> str:
    """Send a conversation to the OpenAI API and return the assistant reply.

    Args:
        messages: List of {"role": ..., "content": ...} dicts (user/assistant turns).
        system_prompt: Override the default system prompt when needed.

    Returns:
        The assistant's text reply.
    """
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    response = await _client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=full_messages,  # type: ignore[arg-type]
        temperature=0.2,
    )
    return response.choices[0].message.content or ""


async def generate_code(description: str, language: str = "") -> str:
    """Generate code from a plain-language description."""
    lang_hint = f" in {language}" if language else ""
    prompt = (
        f"Generate clean, well-commented code{lang_hint} that does the following:\n\n"
        f"{description}\n\n"
        "Only return the code block and a brief explanation below it."
    )
    return await ask([{"role": "user", "content": prompt}])


async def explain_code(code: str) -> str:
    """Explain what a piece of code does."""
    prompt = (
        "Explain what the following code does, step by step, in simple terms:\n\n"
        f"```\n{code}\n```"
    )
    return await ask([{"role": "user", "content": prompt}])


async def debug_code(code: str, error: str = "") -> str:
    """Find bugs in code and suggest fixes."""
    error_section = f"\nError message:\n{error}" if error else ""
    prompt = (
        f"Find and fix bugs in the following code:{error_section}\n\n"
        f"```\n{code}\n```\n\n"
        "List each bug found and provide the corrected code."
    )
    return await ask([{"role": "user", "content": prompt}])


async def review_code(code: str) -> str:
    """Perform a code review and suggest improvements."""
    prompt = (
        "Perform a thorough code review on the following code. "
        "Comment on: correctness, readability, performance, security, and best practices. "
        "Provide an improved version if necessary.\n\n"
        f"```\n{code}\n```"
    )
    return await ask([{"role": "user", "content": prompt}])


async def refactor_code(code: str, goal: str = "") -> str:
    """Refactor code for clarity or performance."""
    goal_hint = f" Focus on: {goal}." if goal else ""
    prompt = (
        f"Refactor the following code to improve its quality.{goal_hint}\n\n"
        f"```\n{code}\n```\n\n"
        "Return the refactored code with a brief explanation of the changes."
    )
    return await ask([{"role": "user", "content": prompt}])
