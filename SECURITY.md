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

### AI brain & privacy
- The AI brain is **opt-in**. The default/recommended backend is **local Ollama** — fully offline,
  no key, nothing leaves your machine.
- If you choose a cloud provider (OpenAI/Anthropic/Gemini/Groq), your **API key is stored locally
  in `~/.pglu/config.json` (plaintext)** and your chat messages are sent to that provider. Use a
  key with minimal scope, and prefer Ollama for full privacy.
- Real actions (opening apps, system info, timers) are executed by the local tool layer, never by
  the model — the model only converses.

### The `cmd` / command runner
- The Run skill executes shell commands you explicitly prefix (`cmd …`, `powershell …`,
  `run command …`). It is **user-triggered only** — the AI model cannot invoke it; the model only
  converses. Output and errors are returned verbatim (never faked).
- Treat it like a terminal: only run commands you understand. Avoid dictating destructive commands
  by voice (mis-hearing is possible). There is a 30-second timeout.
