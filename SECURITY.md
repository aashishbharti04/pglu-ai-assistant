# Security Policy

## Reporting a Vulnerability

Please **do not open a public issue** for security problems. Email
**aashish@marketdoctorsonline.com** with a description, reproduction steps, and impact.
You'll get an acknowledgement within a few days.

## Security & privacy posture

- **Local-first, no cloud brain, no API keys** — knowledge features use only free, key-less public
  APIs (Wikipedia, Open-Meteo). No telemetry or analytics.
- **Voice is on-device** — recognition/synthesis run locally and are optional; audio isn't stored.
- **No `eval`** — arithmetic is parsed and evaluated through a sandboxed AST walker that allows only
  numbers and basic operators (`pglu/util.py`).
- **Limited system control** — the assistant launches known applications and reads system stats; it
  does not delete files or run arbitrary shell input from the user verbatim.
- **Config & notes** are stored locally under `~/.pglu/`. No secrets are committed to the repo.

> Be mindful when extending Pglu with shell-executing skills — never pass raw user text to a shell.
