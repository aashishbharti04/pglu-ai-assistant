# Architecture

Pglu is a small, plugin-based assistant. The core builds one **intent table** from all skills and
dispatches each input to the first matching handler.

```
              ┌──────────── cli.py ────────────┐
              │ interactive / one-shot / doctor │
              │ optional Voice (STT in, TTS out)│
              └───────────────┬─────────────────┘
                              │ text
                       ┌──────▼───────── assistant.py ─────────┐
                       │ build intent table from skills        │
                       │ respond(text): first matching handler │
                       └──────┬────────────────────────────────┘
            ┌─────────┬───────┼─────────┬───────────┬──────────┐
            ▼         ▼       ▼         ▼           ▼          ▼
        system     apps     web    knowledge   productivity   fun     (pglu/skills/*)
            └─────────┴───────┴─────────┴───────────┴──────────┘
                              │ shared
                       util.py (urllib JSON, safe AST math) · config.py (~/.pglu)
```

## The skill contract

Each skill subclasses `Skill` and returns regex **intents**:

```python
def intents(self):
    return [(r"\bbattery\b", self.battery)]   # (pattern, handler)
def battery(self, text, match):
    return "Battery is at 82% (charging)."     # str reply, or None to pass
```

Skills are sorted by `priority` (lower first); within a skill, intent order is preserved. A handler
returning `None` means "not really mine" — dispatch continues to the next intent. This lets, e.g.,
`Apps.open_app` claim `open notepad` while `Web.open_site` returns `None` for unknown apps so the
right skill wins. Math is checked before the Wikipedia “what is …” catch for the same reason.

## Dispatch flow

1. `cli` collects input (typed, or transcribed by `voice.listen()`).
2. `assistant.respond(text)` checks for `help`, then walks the intent table; the first handler
   that returns non-`None` wins; otherwise a friendly fallback (offer to web-search) is returned.
3. `cli` prints the reply and, in voice mode, speaks it via `voice.speak()`.

## Design principles

- **Local-first & key-less** — no cloud LLM, no API keys; Wikipedia/Open-Meteo are free & no-key.
- **Zero core deps** — only `voice` (SpeechRecognition/pyttsx3/PyAudio) and `system` (psutil) extras
  pull in packages, always imported defensively so the assistant runs without them.
- **Safety** — arithmetic via a restricted AST evaluator, never `eval`; OS control limited to
  launching known apps and reading stats.
- **Extensible** — a new ability is one small file + one line in the registry.
- **`doctor`** — borrowed from OpenJarvis: a one-command environment/dependency/network check.
