# Contributing to Pglu AI Assistant

Thanks for helping build a better open assistant! 🤖 New **skills** are the most valuable contribution.

## Development setup

```bash
git clone https://github.com/aashishbharti04/pglu-ai-assistant
cd pglu-ai-assistant
pip install -e ".[dev]"      # pytest + ruff
pip install -e ".[full]"     # optional: voice + system extras

python main.py doctor        # check your environment
pytest -q                    # run tests
ruff check pglu tests        # lint
```

Core features must keep working with **no third-party packages** — only the `voice` and `system`
extras may import optional deps (always behind a `try/except`).

## Project layout

| Path | Responsibility |
|------|----------------|
| `pglu/cli.py` | CLI entry — interactive loop, one-shot, `doctor`, `skills`, `--voice`. |
| `pglu/assistant.py` | Core — builds the intent table from skills and dispatches input. |
| `pglu/skills/` | The skills (system, apps, web, knowledge, productivity, fun) + `base.py`. |
| `pglu/voice.py` | Optional STT/TTS wrappers (graceful fallback). |
| `pglu/util.py` | stdlib HTTP (urllib) + safe AST math. |
| `pglu/config.py` | `~/.pglu/config.json` settings. |

## Adding a skill

1. Create `pglu/skills/yourskill.py` with a `Skill` subclass.
2. Implement `intents()` → list of `(regex, handler)`; `examples()` for the help screen.
3. A handler returns a reply string, or `None` to let other intents try.
4. Register it in `pglu/skills/__init__.py` (`SKILL_CLASSES`).
5. Add a test in `tests/`.

```python
from .base import Skill

class Dictionary(Skill):
    name = "dictionary"
    def intents(self):
        return [(r"\bdefine\s+(?P<w>\w+)", self.define)]
    def define(self, text, m):
        return f"Looking up {m.group('w')}…"
```

## Ground rules

- **Local-first & key-less** — use only free, no-key public APIs (or none). No telemetry.
- **No `eval`** — arithmetic goes through `util.safe_math`.
- **Cross-platform** — guard OS-specific code by `platform.system()`.
- Keep voice optional; every feature must work via typed input.

## Pull requests

1. Fork → feature branch. 2. `pytest -q` and `ruff check` pass. 3. Open a PR using the template.

By contributing you agree your work is licensed under the [MIT License](LICENSE).
