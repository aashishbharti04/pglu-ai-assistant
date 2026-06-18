# Changelog

All notable changes to this project are documented here. Format based on
[Keep a Changelog](https://keepachangelog.com/); versioning follows [SemVer](https://semver.org/).

## [1.0.0] — 2026-06-18

### Added
- **Initial release** of Pglu AI Assistant — a privacy-first, plugin-based desktop assistant.
- **Plugin skill architecture** with 6 skills (~28 intents): System, Apps, Web, Knowledge,
  Productivity, Fun.
- **Voice + text modes** — optional speech input (SpeechRecognition) and output (pyttsx3),
  with full text fallback.
- **Real PC control** — launch native apps (Notepad, Calculator, Settings, Task Manager, VS Code…)
  and open websites.
- **Knowledge** — Wikipedia answers and live weather (Open-Meteo) via key-less APIs; natural-language
  math through a safe AST evaluator (no `eval`).
- **System** — battery, CPU, RAM, disk, IP, and system info (psutil/stdlib).
- **Productivity** — notes and timers/reminders. **Fun** — jokes, coin/dice, random numbers, secure passwords.
- **CLI** — interactive mode, one-shot commands, `pglu doctor` (env/dependency health check), and `pglu skills`.
- **Zero core dependencies** (stdlib only); `voice`/`system`/`full` optional extras. Cross-platform
  (Windows/macOS/Linux), UTF-8-safe console output.
- Open-source project files: README, MIT LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, tests,
  issue/PR templates, ARCHITECTURE doc, and CI (ruff + pytest) workflow.
