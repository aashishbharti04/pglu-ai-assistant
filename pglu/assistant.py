"""The assistant core: builds the intent table from skills and dispatches input."""

from __future__ import annotations

import re

from . import __version__
from .skills import build_skills

EXIT_WORDS = {"exit", "quit", "bye", "goodbye", "stop", "shutdown pglu"}


class Assistant:
    def __init__(self, config, voice=None):
        self.config = config
        self.voice = voice
        self.timers = []
        self.skills = sorted(build_skills(self), key=lambda s: s.priority)
        # flat intent table: (compiled_regex, handler, skill), preserving intra-skill order
        self.intents = []
        for sk in self.skills:
            for pattern, handler in sk.intents():
                self.intents.append((re.compile(pattern, re.I), handler, sk))

    def is_exit(self, text):
        return text.strip().lower() in EXIT_WORDS

    def respond(self, text):
        text = (text or "").strip()
        if not text:
            return ""
        if re.search(r"\b(help|what can you do|commands|capabilities)\b", text, re.I):
            return self.help()
        for rx, handler, _sk in self.intents:
            m = rx.search(text)
            if not m:
                continue
            try:
                reply = handler(text, m)
            except Exception as e:  # a skill should never crash the loop
                return f"Sorry, that failed: {e}"
            if reply is not None:   # None = "not really mine", keep trying
                return reply
        return (f"I'm not sure how to help with that. Say 'help' to see what I can do, "
                f"or 'search {text}' to look it up.")

    def help(self):
        lines = [f"🤖 {self.config.name} can help with:"]
        for sk in self.skills:
            ex = sk.examples()
            if ex:
                lines.append(f"\n• {sk.name.title()}: " + " · ".join(f"“{e}”" for e in ex[:4]))
        lines.append("\nSay 'exit' to quit.")
        return "\n".join(lines)

    def doctor(self):
        """Environment + dependency health check (à la `jarvis doctor`)."""
        import platform
        rows = [("Pglu version", __version__), ("Python", platform.python_version()),
                ("Platform", f"{platform.system()} {platform.release()}")]

        def probe(mod):
            try:
                __import__(mod); return "✓ installed"
            except Exception:
                return "✗ missing (optional)"
        rows += [("psutil (system info)", probe("psutil")),
                 ("SpeechRecognition (voice in)", probe("speech_recognition")),
                 ("pyttsx3 (voice out)", probe("pyttsx3")),
                 ("PyAudio (microphone)", probe("pyaudio"))]
        # network probe
        try:
            from .util import get_json
            get_json("https://api.ipify.org?format=json", timeout=5)
            rows.append(("Internet", "✓ reachable"))
        except Exception:
            rows.append(("Internet", "✗ offline (web answers/weather won't work)"))
        rows.append(("Skills loaded", str(len(self.skills))))
        rows.append(("Intents", str(len(self.intents))))
        w = max(len(k) for k, _ in rows)
        return "🩺 Pglu doctor\n" + "\n".join(f"  {k.ljust(w)} : {v}" for k, v in rows)
