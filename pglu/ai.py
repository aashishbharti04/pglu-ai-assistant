"""Pluggable LLM 'brain'. Local-first (Ollama, no key) or any major API (key stored locally).
All HTTP via urllib — no third-party packages."""

from __future__ import annotations

import json
import urllib.request

DEFAULT_MODELS = {
    "ollama": "llama3.2",
    "openai": "gpt-4o-mini",
    "groq": "llama-3.3-70b-versatile",
    "openrouter": "openai/gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-latest",
    "gemini": "gemini-1.5-flash",
}
OPENAI_BASE = {
    "openai": "https://api.openai.com/v1",
    "groq": "https://api.groq.com/openai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
}


def normalize_provider(s):
    """Map friendly/loose input ('ollama (local, free)', 'Claude', 'gpt') to a canonical id."""
    s = (s or "").strip().lower()
    if not s:
        return "auto"
    if "ollama" in s:
        return "ollama"
    if s.startswith("none") or s == "off":
        return "none"
    if "auto" in s:
        return "auto"
    if "anthropic" in s or "claude" in s:
        return "anthropic"
    if "openrouter" in s:
        return "openrouter"
    if "groq" in s:
        return "groq"
    if "openai" in s or "gpt" in s or "chatgpt" in s:
        return "openai"
    if "gemini" in s or "google" in s:
        return "gemini"
    return s


def needs_key(provider):
    return normalize_provider(provider) not in ("ollama", "none", "auto")


def _post(url, payload, headers, timeout=60):
    data = json.dumps(payload).encode("utf-8")
    h = {"Content-Type": "application/json", **headers}
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


class Brain:
    def __init__(self, cfg):
        self.cfg = cfg
        self.provider = normalize_provider(cfg.ai_provider)
        self.key = (cfg.ai_api_key or "").strip()
        self.model = (cfg.ai_model or "").strip()
        self._avail = None

    def effective_provider(self):
        if self.provider not in ("", "auto"):
            return self.provider
        return "ollama" if not self.key else "openai"

    def _model(self):
        return self.model or DEFAULT_MODELS.get(self.effective_provider(), "llama3.2")

    def available(self):
        if self._avail is not None:
            return self._avail
        p = self.effective_provider()
        if p == "ollama":
            try:
                urllib.request.urlopen("http://localhost:11434/api/tags", timeout=1.5)
                self._avail = True
            except Exception:
                self._avail = False
        elif p == "none":
            self._avail = False
        else:
            self._avail = bool(self.key)
        return self._avail

    def reply(self, system, messages):
        """messages: list of {'role':'user'|'assistant','content':str}. Returns text or None."""
        p = self.effective_provider()
        try:
            if p == "ollama":
                return self._ollama(system, messages)
            if p in OPENAI_BASE:
                return self._openai(p, system, messages)
            if p == "anthropic":
                return self._anthropic(system, messages)
            if p in ("gemini", "google"):
                return self._gemini(system, messages)
        except Exception:
            return None
        return None

    # ---- providers ----
    def _ollama(self, system, messages):
        d = _post("http://localhost:11434/api/chat", {
            "model": self._model(),
            "messages": [{"role": "system", "content": system}] + messages,
            "stream": False,
        }, {})
        return (d.get("message") or {}).get("content", "").strip() or None

    def _openai(self, provider, system, messages):
        d = _post(f"{OPENAI_BASE[provider]}/chat/completions", {
            "model": self._model(),
            "messages": [{"role": "system", "content": system}] + messages,
            "temperature": 0.7,
        }, {"Authorization": f"Bearer {self.key}"})
        return d["choices"][0]["message"]["content"].strip() or None

    def _anthropic(self, system, messages):
        d = _post("https://api.anthropic.com/v1/messages", {
            "model": self._model(),
            "max_tokens": 600,
            "system": system,
            "messages": messages,
        }, {"x-api-key": self.key, "anthropic-version": "2023-06-01"})
        return "".join(b.get("text", "") for b in d.get("content", [])).strip() or None

    def _gemini(self, system, messages):
        contents = [{"role": ("model" if m["role"] == "assistant" else "user"),
                     "parts": [{"text": m["content"]}]} for m in messages]
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/{self._model()}"
               f":generateContent?key={self.key}")
        d = _post(url, {"systemInstruction": {"parts": [{"text": system}]}, "contents": contents}, {})
        return "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"]).strip() or None
