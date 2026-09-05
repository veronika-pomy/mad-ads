"""Entrypoint: Day 1 scope only — verifies imports wire together.

Later days add: Phase A (draft/pick/send) and Phase B (poll loop -> Closer).
"""
import telegram_tools  # noqa: F401
import conversation_store  # noqa: F401

if __name__ == "__main__":
    print("mad-ads scaffold OK: telegram_tools and conversation_store import cleanly.")
