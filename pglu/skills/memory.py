"""Memory controls — clear what the assistant remembers across sessions."""

from __future__ import annotations

from .base import Skill


class Memory(Skill):
    name = "memory"
    priority = 15  # before chat/other skills

    def intents(self):
        return [
            (r"\b(forget (everything|all|our (chat|conversation|talk)|me)|"
             r"clear (your |our )?(memory|chat|history)|wipe (your )?memory|start fresh)\b", self.forget),
        ]

    def examples(self):
        return ["forget everything", "clear our chat history"]

    def forget(self, text, m):
        self.ctx.clear_memory()
        return "Done — I've cleared what I remembered from our conversations."
