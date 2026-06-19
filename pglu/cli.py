"""Command-line entry point for Pglu AI Assistant."""

from __future__ import annotations

import argparse

from . import __version__
from .config import Config
from .assistant import Assistant


def main(argv=None):
    # Make emoji/unicode output safe on legacy consoles (e.g. Windows cp1252).
    import sys
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        prog="pglu",
        description="Pglu AI Assistant — a privacy-first, plugin-based desktop assistant.")
    parser.add_argument("command", nargs="*",
                        help="A one-shot command, or 'doctor' / 'skills'. Omit for interactive mode.")
    parser.add_argument("--voice", action="store_true", help="Enable voice input/output (needs optional deps).")
    parser.add_argument("--version", action="store_true", help="Show version and exit.")
    args = parser.parse_args(argv)

    if args.version:
        print(f"Pglu AI Assistant {__version__}")
        return

    cfg = Config.load()

    voice = None
    if args.voice:
        from .voice import Voice
        voice = Voice(cfg)
        if not voice.available:
            print('⚠️  Voice dependencies not found — staying in text mode.\n'
                  '    Install with:  pip install "pglu-ai-assistant[voice]"')
            voice = None

    one = args.command[0].lower() if args.command else ""

    # first-run / identity + persona + AI provider wizard
    if one == "setup" and len(args.command) == 1:
        _setup(cfg)
        return

    # GUI window (desktop app); `gui min` starts minimized (used by autostart)
    if one == "gui" and len(args.command) <= 2:
        from .gui import run_gui
        run_gui(minimized=(len(args.command) == 2 and args.command[1].lower() == "min"))
        return

    # start automatically on login:  `pglu autostart`  /  `pglu autostart off`
    if one == "autostart" and len(args.command) <= 2:
        from .desktop import install_autostart, remove_autostart
        off = len(args.command) == 2 and args.command[1].lower() in ("off", "disable", "remove")
        try:
            if off:
                p = remove_autostart()
                print("✓ Autostart disabled." if p else "Autostart was not set.")
            else:
                p = install_autostart(minimized=True)
                print(f"✓ Pglu will now start (minimized) when you log in:\n    {p}\n"
                      "  Disable any time with:  pglu autostart off")
        except Exception as e:
            print(f"Couldn't change autostart automatically: {e}")
        return

    # create a clickable desktop shortcut/icon
    if one in ("install-shortcut", "shortcut") and len(args.command) == 1:
        from .desktop import install_shortcut
        try:
            path = install_shortcut()
            print(f"✓ Desktop shortcut created:\n    {path}\n"
                  "Double-click 'Pglu AI Assistant' on your Desktop to open the window.")
        except Exception as e:
            print(f"Couldn't create the shortcut automatically: {e}\n"
                  "You can still launch the app with:  pglu gui")
        return

    from .ai import Brain
    assistant = Assistant(cfg, voice=voice, brain=Brain(cfg))

    if one == "doctor" and len(args.command) == 1:
        print(assistant.doctor())
        return
    if one == "skills" and len(args.command) == 1:
        print(assistant.help())
        return

    if args.command:  # one-shot
        reply = assistant.respond(" ".join(args.command))
        print(reply)
        if voice:
            voice.speak(reply)
        return

    _interactive(assistant, voice, cfg)


def _setup(cfg):
    from .persona import persona_list
    from .ai import Brain

    print("⚙  Pglu setup — press Enter to keep the current value.\n")

    def ask(label, cur):
        v = input(f"  {label} [{cur}]: ").strip()
        return v or cur

    cfg.name = ask("AI assistant's name", cfg.name)
    cfg.user_name = ask("Your name", cfg.user_name)
    cfg.user_about = ask("One line about you (role, interests)", cfg.user_about)

    print("\n  Personality styles:")
    pl = persona_list()
    for i, (pid, nm) in enumerate(pl, 1):
        print(f"    {i}. {nm}  ({pid})")
    sel = input(f"  Pick a number/id, or type your own custom style [{cfg.persona}]: ").strip()
    if sel:
        ids = [pid for pid, _ in pl]
        if sel.isdigit() and 1 <= int(sel) <= len(pl):
            cfg.persona, cfg.custom_persona = pl[int(sel) - 1][0], ""
        elif sel in ids:
            cfg.persona, cfg.custom_persona = sel, ""
        else:
            cfg.custom_persona = sel

    from .ai import normalize_provider, needs_key
    print("\n  AI brain provider — type one word:  ollama (local, free) | openai | anthropic | gemini | groq | none")
    cfg.ai_provider = normalize_provider(ask("Provider", normalize_provider(cfg.ai_provider) or "ollama"))
    if needs_key(cfg.ai_provider):
        cfg.ai_api_key = ask("API key (stored locally in ~/.pglu/config.json)", cfg.ai_api_key)
    else:
        print("  (No API key needed for Ollama — using your local models.)")
    cfg.ai_model = ask("Model (blank = sensible default)", cfg.ai_model)

    cfg.save()
    print("\n✓ Saved to ~/.pglu/config.json")
    b = Brain(cfg)
    if b.available():
        print(f"🧠 AI brain ready via {b.effective_provider()}. Run `pglu` or `pglu gui` and just talk!")
    else:
        print("⚠️  AI brain not reachable yet. For local AI: install Ollama (ollama.com) and run "
              "`ollama pull llama3.2`. Or choose an API provider + key. Pglu still works in command mode.")


def _interactive(assistant, voice, cfg):
    print(f"🤖 {cfg.name} AI Assistant is online. Type a command — or 'help', 'exit'.")
    if voice:
        voice.speak(f"{cfg.name} online. How can I help, {cfg.user_name}?")
    while True:
        try:
            if voice and voice.stt_ok:
                print("\n🎙️  Listening…")
                text = voice.listen()
                if text:
                    print(f"You: {text}")
                else:
                    text = input("(didn't catch that — type) You: ")
            else:
                text = input("\nYou: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not text.strip():
            continue
        if assistant.is_exit(text):
            print(f"{cfg.name}: Goodbye!")
            if voice:
                voice.speak("Goodbye!")
            break
        reply = assistant.respond(text)
        print(f"{cfg.name}: {reply}")
        if voice:
            voice.speak(reply)


if __name__ == "__main__":
    main()
