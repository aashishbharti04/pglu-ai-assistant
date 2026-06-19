"""Memory controls — clear what the assistant remembers across sessions."""

from __future__ import annotations

from .base import Skill


class Memory(Skill):
    name = "memory"
    priority = 15  # before chat/other skills

    def intents(self):
        return [
            (r"^\s*(?:new chat|start (?:a )?new (?:chat|conversation)|new conversation|"
             r"reset chat|start over|fresh start)\b", self.new_chat),
            (r"\b(forget (everything|all|our (chat|conversation|talk)|me)|"
             r"clear (your |our )?(memory|chat|history)|wipe (your )?memory)\b", self.forget),
        ]

    def examples(self):
        return ["new chat", "forget everything", "clear our chat history"]

    def new_chat(self, text, m):
        self.ctx.clear_memory()
        return "🆕 Started a new chat — clean slate. What would you like to talk about?"

    def forget(self, text, m):
        self.ctx.clear_memory()
        return "Done — I've cleared what I remembered from our conversations."
