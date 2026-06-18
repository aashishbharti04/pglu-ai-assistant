"""The assistant core: builds the intent table from skills and dispatches input."""

from __future__ import annotations

import re

from . import __version__
from .skills import build_skills

EXIT_WORDS = {"exit", "quit", "bye", "goodbye", "stop", "shutdown pglu"}


class Assistant:
    def __init__(self, config, voice=None, brain=None):
        self.config = config
        self.voice = voice
        self.brain = brain          # optional LLM brain (pglu.ai.Brain)
        self.history = []           # rolling chat memory: [{role, content}, ...]
        self.timers = []
        self.skills = sorted(build_skills(self), key=lambda s: s.priority)
        # flat intent table: (compiled_regex, handler, skill), preserving intra-skill order
        self.intents = []
        for sk in self.skills:
            for pattern, handler in sk.intents():
                self.intents.append((re.compile(pattern, re.I), handler, sk))

    def is_exit(self, text):
        return text.strip().lower() in EXIT_WORDS

    @property
    def brain_available(self):
        try:
            return bool(self.brain) and self.brain.available()
        except Exception:
            return False

    def respond(self, text):
        text = (text or "").strip()
        if not text:
            return ""
        if text.lower() in ("help", "commands", "menu", "skills"):
            return self.help()
        # 1) tools: skills that DO something or give precise local facts
        for rx, handler, _sk in self.intents:
            m = rx.search(text)
            if not m:
                continue
            try:
                reply = handler(text, m)
            except Exception as e:  # a skill should never crash the loop
                return f"Sorry, that failed: {e}"
            if reply is not None:   # None = "not mine" (or handed to the brain), keep trying
                return reply
        # 2) conversation: the LLM brain answers in-character
        if self.brain_available:
            out = self._chat(text)
            if out:
                return out
        # 3) offline fallback
        return (f"I'm not sure how to help with that. Say 'help' to see what I can do, "
                f"or 'search {text}' to look it up. (Tip: run `pglu setup` to give me an AI brain "
                "so I can really chat.)")

    def _chat(self, text):
        from .persona import build_system_prompt
        system = build_system_prompt(self.config)
        msgs = self.history[-8:] + [{"role": "user", "content": text}]
        out = self.brain.reply(system, msgs)
        if out:
            self.history.append({"role": "user", "content": text})
            self.history.append({"role": "assistant", "content": out})
            self.history = self.history[-12:]
        return out

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

        def _okmod(mod):
            try:
                __import__(mod); return True
            except Exception:
                return False

        def probe(mod):
            return "✓ installed" if _okmod(mod) else "✗ missing (optional)"
        rows += [("psutil (system info)", probe("psutil")),
                 ("pyttsx3 (voice out)", probe("pyttsx3")),
                 ("SpeechRecognition (voice in)", probe("speech_recognition")),
                 ("PyAudio (microphone)", probe("pyaudio")),
                 ("pynput (hotkey wake)", probe("pynput")),
                 ("sounddevice+numpy (clap wake)", "✓ installed" if (_okmod("sounddevice") and _okmod("numpy")) else "✗ missing (optional)")]
        # network probe
        try:
            from .util import get_json
            get_json("https://api.ipify.org?format=json", timeout=5)
            rows.append(("Internet", "✓ reachable"))
        except Exception:
            rows.append(("Internet", "✗ offline (web answers/weather won't work)"))
        if self.brain is not None:
            try:
                rows.append(("AI brain", f"{self.brain.effective_provider()} · "
                             + ("✓ ready" if self.brain_available else "✗ not reachable")))
            except Exception:
                rows.append(("AI brain", "error"))
        else:
            rows.append(("AI brain", "not configured (run `pglu setup`)"))
        rows.append(("Persona", self.config.custom_persona and "custom" or self.config.persona))
        rows.append(("Skills loaded", str(len(self.skills))))
        rows.append(("Intents", str(len(self.intents))))
        w = max(len(k) for k, _ in rows)
        return "🩺 Pglu doctor\n" + "\n".join(f"  {k.ljust(w)} : {v}" for k, v in rows)
