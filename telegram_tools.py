"""Telegram Bot API helpers: outbound send + inbound long-polling.

Uses raw `requests` against the Bot API (see PLAN.md §5) instead of a
wrapper library.
"""
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


def _api_url(method: str) -> str:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set (check .env)")
    return f"{API_BASE}/{method}"


def get_me() -> dict:
    resp = requests.get(_api_url("getMe"), timeout=10)
    resp.raise_for_status()
    return resp.json()


def delete_webhook() -> dict:
    resp = requests.post(_api_url("deleteWebhook"), timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_webhook_info() -> dict:
    resp = requests.get(_api_url("getWebhookInfo"), timeout=10)
    resp.raise_for_status()
    return resp.json()


def send_telegram_message(chat_id: str, text: str) -> dict:
    resp = requests.post(
        _api_url("sendMessage"),
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def poll_updates(on_message, poll_interval_seconds: float = 2.0):
    """Long-poll getUpdates and invoke on_message(chat_id, text, update) for each new message.

    Blocks forever; run in its own thread/process.
    """
    offset = None
    while True:
        params = {"timeout": 30}
        if offset is not None:
            params["offset"] = offset
        resp = requests.get(_api_url("getUpdates"), params=params, timeout=40)
        resp.raise_for_status()
        result = resp.json().get("result", [])
        for update in result:
            offset = update["update_id"] + 1
            message = update.get("message")
            if not message or "text" not in message:
                continue
            chat_id = str(message["chat"]["id"])
            on_message(chat_id, message["text"], update)
        if not result:
            time.sleep(poll_interval_seconds)
