<div align="center">

# 🤖 Pglu AI Assistant

### A privacy-first, plugin-based desktop assistant — your own Jarvis, in Python

Talk or type to **open apps, search the web, answer questions, check your system, set timers,
take notes, and more.** Core features run on the **Python standard library alone** — voice and
system-info are optional extras. Local-first: no cloud brain, no API keys.

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=0b0f17">
  <img alt="Core deps" src="https://img.shields.io/badge/Core%20deps-ZERO-22c55e?style=for-the-badge&labelColor=0b0f17">
  <img alt="Cross platform" src="https://img.shields.io/badge/Win%20%C2%B7%20macOS%20%C2%B7%20Linux-cross--platform-8b5cf6?style=for-the-badge&labelColor=0b0f17">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-f59e0b?style=for-the-badge&labelColor=0b0f17">
</p>

</div>

> **Inspired by** [sukeesh/Jarvis](https://github.com/sukeesh/Jarvis) (plugin CLI assistant),
> [open-jarvis/OpenJarvis](https://github.com/open-jarvis/OpenJarvis) (local-first ethos + a
> `doctor` health check), and [Priler/jarvis](https://github.com/Priler/jarvis) (offline,
> privacy-first voice) — re-imagined as a clean, dependency-light Python package.

---

## 📖 Overview

Pglu AI Assistant is a real desktop assistant that controls your PC and answers your questions —
from a terminal, by **typing or speaking**. It uses a small **plugin "skill" architecture**: each
skill registers regex intents and a handler, so adding new abilities is a few lines. There's no
cloud LLM and no keys: knowledge comes from key-less public APIs (Wikipedia, Open-Meteo) and
everything else runs locally.

## 📸 Preview

<div align="center">
  <img src="docs/screenshot.svg" alt="Terminal session showing Pglu AI Assistant answering commands" width="760">
</div>

## ✨ Features

- 🧩 **Plugin skill architecture** — 6 skills, ~28 intents; add your own in a few lines
- 🗣️ **Voice *and* text** — speak (SpeechRecognition) and hear replies (pyttsx3), or just type
- 🖥️ **Real PC control** — launch apps (Notepad, Calculator, Settings, Task Manager, VS Code…), open sites
- 🔎 **Web** — Google / YouTube search, open any website
- 🧠 **Answers** — Wikipedia summaries (“who is…”, “what is…”), live **weather** for any city
- 🧮 **Math** — natural language (“what is 24 times 7”) via a safe AST evaluator (no `eval`)
- ⚙️ **System** — battery, CPU, RAM, disk, IP, system info (via `psutil` / stdlib)
- 📝 **Productivity** — notes and timers/reminders
- 🎲 **Fun** — jokes, coin flip, dice, random numbers, secure password generator
- 🩺 **`pglu doctor`** — environment & dependency health check
- 🔒 **Privacy-first & local** — no cloud brain, no API keys; key-less public APIs only
- 🪶 **Zero core dependencies** — extras (`voice`, `system`) are opt-in

## 🚀 Installation

```bash
git clone https://github.com/aashishbharti04/pglu-ai-assistant
cd pglu-ai-assistant

# core features need nothing extra — just run it:
python main.py "what is 25 times 4"

# install as a command + optional extras:
pip install -e .                 # adds the `pglu` command (core only)
pip install -e ".[full]"         # + voice (mic/speech) + system info
```

Requires **Python 3.9+**. Voice input also needs a microphone (and PyAudio); on Linux you may
need `sudo apt install portaudio19-dev` before `pip install PyAudio`.

## 🕹️ Usage

```bash
pglu                       # interactive text mode
pglu --voice               # interactive voice mode (needs [voice] extra)
pglu doctor                # environment & dependency check
pglu skills                # list everything Pglu can do
pglu "open notepad"        # one-shot command
python main.py "weather in Mumbai"   # without installing
```

### Things to say or type

| Category | Examples |
|----------|----------|
| Apps | `open notepad` · `open calculator` · `launch task manager` · `open settings` |
| Web | `open youtube` · `open github.com` · `search for best laptops` · `youtube lofi beats` |
| Knowledge | `what time is it` · `what's the date` · `who is Ada Lovelace` · `what is gravity` |
| Weather | `weather in Delhi` |
| Math | `what is 24 times 7` · `calculate 100 divided by 4` |
| System | `battery` · `cpu usage` · `how much ram` · `disk space` · `my ip` · `system info` |
| Productivity | `take a note: buy milk` · `read my notes` · `set a timer for 5 minutes` |
| Fun | `tell me a joke` · `flip a coin` · `roll a dice` · `random number 1 to 100` · `generate a password 16` |

## ⚙️ Configuration

Settings live in `~/.pglu/config.json` (assistant name, user name, wake word, TTS rate, default
city). Notes are saved alongside it. Nothing is sent anywhere.

## 🧩 Adding a skill

Create a `Skill` subclass in `pglu/skills/`, register intents, and add it to `SKILL_CLASSES`:

```python
from .base import Skill

class Hello(Skill):
    name = "hello"
    def intents(self):
        return [(r"\bgreet me\b", self.greet)]
    def greet(self, text, m):
        return f"Hello, {self.ctx.config.user_name}!"
```

A handler returns a string (the reply) or `None` to let other intents try. See
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## ❓ FAQ

**Does it need an API key or the internet?** No keys ever. Most features are offline; only
Wikipedia and weather make (key-less) web calls.

**Voice not working?** Install the `voice` extra and ensure a mic + PyAudio. Voice is optional —
typing always works.

**Is it safe?** Math uses a sandboxed AST evaluator (never `eval`); there are no secrets; system
control is limited to launching apps and reading stats.

## 🤝 Contributing

PRs welcome — new skills especially! See [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Code of Conduct](CODE_OF_CONDUCT.md). Security: [SECURITY.md](SECURITY.md).

## 📄 License

[MIT](LICENSE) © Aashish Bharti — free for educational, learning, and community use.

---

<div align="center">

### 📬 Contact & Connect

**Email:** [aashish@marketdoctorsonline.com](mailto:aashish@marketdoctorsonline.com)

[LinkedIn](https://in.linkedin.com/in/aashana1012) ·
[GitHub](https://github.com/aashishbharti04) ·
[YouTube](https://www.youtube.com/@CodeWithAsur) ·
[Instagram](https://www.instagram.com/asurwave1012)

<sub>© Pglu AI Assistant. All rights reserved. · This project is open source and available for
educational, learning, and community contributions.</sub>

</div>
