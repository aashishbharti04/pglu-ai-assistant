"""Productivity: notes and timers/reminders."""

from __future__ import annotations

import json
import threading

from .base import Skill
from ..config import data_path

NOTES_FILE = data_path("notes.json")
_UNIT = {"second": 1, "seconds": 1, "sec": 1, "minute": 60, "minutes": 60, "min": 60, "hour": 3600, "hours": 3600}


def _load():
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save(n):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(n, f, indent=2)


class Productivity(Skill):
    name = "productivity"
    priority = 35

    def intents(self):
        return [
            (r"\b(?:take a note|make a note|note that|remember that|note|remember)\b[:\s]+(?P<n>.+)", self.add_note),
            (r"\b(?:read|show|list|what are) (?:my )?notes\b", self.read_notes),
            (r"\b(?:clear|delete|remove) (?:my |all )?notes\b", self.clear_notes),
            (r"\b(?:set a |start a )?(?:timer|reminder)\b.*?(?P<num>\d+)\s*(?P<unit>seconds?|sec|minutes?|min|hours?)(?:\s+(?:to|for|about)\s+(?P<msg>.+))?", self.timer),
            (r"\bremind me (?:to )?(?P<msg>.+?)\s+in\s+(?P<num>\d+)\s*(?P<unit>seconds?|sec|minutes?|min|hours?)", self.timer),
        ]

    def examples(self):
        return ["take a note: buy milk", "read my notes", "set a timer for 5 minutes",
                "remind me to stretch in 30 minutes"]

    def add_note(self, text, m):
        notes = _load()
        notes.append(m.group("n").strip())
        _save(notes)
        return "Noted."

    def read_notes(self, text, m):
        notes = _load()
        if not notes:
            return "You don't have any notes yet."
        return "Your notes:\n" + "\n".join(f"  {i + 1}. {n}" for i, n in enumerate(notes))

    def clear_notes(self, text, m):
        _save([])
        return "All notes cleared."

    def timer(self, text, m):
        n = int(m.group("num"))
        secs = n * _UNIT.get(m.group("unit"), 60)
        msg = (m.groupdict().get("msg") or "").strip()
        label = msg or "timer"

        def done():
            note = f"\n⏰ Time's up — {label}!"
            print(note)
            if self.ctx.voice:
                self.ctx.voice.speak(f"Time's up. {msg}" if msg else "Your timer is up.")

        t = threading.Timer(secs, done)
        t.daemon = True
        t.start()
        self.ctx.timers.append(t)
        unit = m.group("unit")
        return f"Okay — I'll remind you in {n} {unit}" + (f" to {msg}." if msg else ".")
