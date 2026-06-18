"""Skill base class. A skill exposes one or more regex intents → handler functions."""

from __future__ import annotations

import re


class Skill:
    name = "skill"
    priority = 50  # lower runs first when matching

    def __init__(self, ctx):
        self.ctx = ctx  # AppContext: config, voice, etc.

    def intents(self):
        """Return a list of (regex_pattern, handler) tuples.
        handler(text, match) -> str (the reply)."""
        return []

    def examples(self):
        """Return a list of example phrases for the help screen."""
        return []

    # convenience
    @staticmethod
    def rx(pattern):
        return re.compile(pattern, re.I)
