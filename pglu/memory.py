"""Persistent conversation memory — stored at ~/.pglu/memory.json so Pglu remembers
past chats across sessions."""

from __future__ import annotations

import json
import os

from .config import data_path

MEM_FILE = data_path("memory.json")
LIMIT = 50  # keep the most recent N messages on disk


def load(limit: int = LIMIT):
    try:
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data[-limit:] if isinstance(data, list) else []
    except Exception:
        return []


def save(history, limit: int = LIMIT):
    try:
        with open(MEM_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-limit:], f, ensure_ascii=False, indent=0)
    except Exception:
        pass


def clear():
    try:
        os.remove(MEM_FILE)
    except Exception:
        pass
