"""Tests for utils/formatting.py."""

from utils.formatting import escape_mdv2, split_long_message, truncate


class TestTruncate:
    def test_short_text_unchanged(self):
        text = "hello world"
        assert truncate(text, max_length=100) == text

    def test_long_text_truncated(self):
        text = "a" * 100
        result = truncate(text, max_length=10)
        assert len(result) == 10
        assert result.endswith("...")

    def test_exact_length_unchanged(self):
        text = "a" * 50
        assert truncate(text, max_length=50) == text


class TestSplitLongMessage:
    def test_short_message_not_split(self):
        text = "Short message"
        chunks = split_long_message(text, max_length=100)
        assert chunks == [text]

    def test_long_message_split(self):
        lines = ["line " + str(i) + "\n" for i in range(50)]
        text = "".join(lines)
        chunks = split_long_message(text, max_length=100)
        assert len(chunks) > 1
        # All content preserved
        assert "".join(chunks) == text

    def test_does_not_split_inside_code_block(self):
        """A code block that fits within max_length should stay in one chunk."""
        code_block = "```python\n" + "x = 1\n" * 5 + "```\n"
        # Slightly less than max_length so it stays whole
        chunks = split_long_message(code_block, max_length=len(code_block) + 50)
        assert len(chunks) == 1

    def test_empty_string(self):
        chunks = split_long_message("", max_length=100)
        assert chunks == [""]


class TestEscapeMdv2:
    def test_escapes_special_chars(self):
        assert escape_mdv2(".") == "\\."
        assert escape_mdv2("!") == "\\!"
        assert escape_mdv2("_") == "\\_"
        assert escape_mdv2("*") == "\\*"

    def test_plain_text_unchanged(self):
        assert escape_mdv2("hello world") == "hello world"

    def test_multiple_special_chars(self):
        result = escape_mdv2("Hello. World!")
        assert result == "Hello\\. World\\!"
