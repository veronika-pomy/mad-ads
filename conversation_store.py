"""Tiny JSON-backed conversation history store, keyed by chat_id (PLAN.md §5)."""
import json
import os
import threading
from datetime import datetime, timezone

_LOCK = threading.Lock()
_DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "conversations.json")


def _load(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save(path: str, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def append_message(chat_id: str, role: str, text: str, path: str = _DEFAULT_PATH) -> None:
    """role is 'inbound' (from buyer) or 'outbound' (from a bot agent)."""
    with _LOCK:
        data = _load(path)
        history = data.setdefault(str(chat_id), [])
        history.append(
            {
                "role": role,
                "text": text,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
        )
        _save(path, data)


def get_history(chat_id: str, path: str = _DEFAULT_PATH) -> list:
    with _LOCK:
        data = _load(path)
        return list(data.get(str(chat_id), []))
