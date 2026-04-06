"""Tests for utils/history.py (ConversationHistory)."""

from utils.history import ConversationHistory


class TestConversationHistory:
    def setup_method(self):
        self.hist = ConversationHistory(max_turns=3)

    def test_add_and_get_messages(self):
        self.hist.add_user(1, "Hello")
        self.hist.add_assistant(1, "Hi there!")
        messages = self.hist.get(1)
        assert messages == [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

    def test_different_users_isolated(self):
        self.hist.add_user(1, "User 1 message")
        self.hist.add_user(2, "User 2 message")
        assert len(self.hist.get(1)) == 1
        assert len(self.hist.get(2)) == 1
        assert self.hist.get(1)[0]["content"] == "User 1 message"
        assert self.hist.get(2)[0]["content"] == "User 2 message"

    def test_clear_removes_history(self):
        self.hist.add_user(1, "Hello")
        self.hist.add_assistant(1, "Hi")
        self.hist.clear(1)
        assert self.hist.get(1) == []

    def test_history_bounded_by_max_turns(self):
        # max_turns=3 means deque maxlen=6 (3 user + 3 assistant)
        for i in range(10):
            self.hist.add_user(1, f"msg {i}")
            self.hist.add_assistant(1, f"reply {i}")
        messages = self.hist.get(1)
        # Should only contain last 3 pairs (6 messages)
        assert len(messages) == 6

    def test_empty_history_for_new_user(self):
        assert self.hist.get(999) == []
