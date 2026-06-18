"""Fun & small talk: greetings, jokes, coin/dice, random number, password generator."""

from __future__ import annotations

import random
import secrets
import string

from .base import Skill

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "I told my computer I needed a break — now it keeps sending me KitKat ads.",
    "Why did the developer go broke? He used up all his cache.",
    "There are 10 kinds of people: those who understand binary and those who don't.",
    "Why was the function sad after the party? It didn't get called.",
    "A SQL query walks into a bar, approaches two tables and asks: may I join you?",
]


class Fun(Skill):
    name = "fun"
    priority = 40

    def intents(self):
        return [
            (r"^\s*(?:hi|hello|hey|yo|namaste|hola|good (?:morning|evening|afternoon))\b", self.greet),
            (r"\b(?:thanks|thank you|thx)\b", self.thanks),
            (r"\b(?:who are you|your name|what are you|introduce yourself)\b", self.about),
            (r"\b(?:joke|make me laugh|something funny)\b", self.joke),
            (r"\b(?:flip a coin|coin toss|toss a coin)\b", self.coin),
            (r"\b(?:roll (?:a )?(?:dice|die)|throw (?:a )?dice)\b", self.dice),
            (r"\brandom number(?:\s+between\s+(?P<a>\d+)\s+(?:and|to)\s+(?P<b>\d+))?", self.rnd),
            (r"\b(?:random |strong |generate (?:a )?)?password(?:\s+(?P<len>\d+))?", self.password),
        ]

    def examples(self):
        return ["tell me a joke", "flip a coin", "roll a dice", "random number between 1 and 100",
                "generate a password 16"]

    def greet(self, text, m):
        return random.choice([f"Hello {self.ctx.config.user_name}! How can I help?",
                              "Hi there — what can I do for you?",
                              f"{self.ctx.config.name} at your service."])

    def thanks(self, text, m):
        return random.choice(["You're welcome!", "Anytime!", "Happy to help."])

    def about(self, text, m):
        return (f"I'm {self.ctx.config.name} — your privacy-first desktop assistant. I can open apps, "
                "search the web, answer questions, check your system, set timers, and more. Say 'help'.")

    def joke(self, text, m):
        return random.choice(JOKES)

    def coin(self, text, m):
        return "🪙 " + random.choice(["Heads!", "Tails!"])

    def dice(self, text, m):
        return f"🎲 You rolled a {random.randint(1, 6)}."

    def rnd(self, text, m):
        a = int(m.group("a")) if m.group("a") else 1
        b = int(m.group("b")) if m.group("b") else 100
        lo, hi = min(a, b), max(a, b)
        return f"🔢 {random.randint(lo, hi)} (between {lo} and {hi})."

    def password(self, text, m):
        n = max(8, min(64, int(m.group("len")) if m.group("len") else 16))
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*-_"
        pw = "".join(secrets.choice(alphabet) for _ in range(n))
        return f"🔐 {pw}"
