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

    # GUI window (desktop app)
    if one == "gui" and len(args.command) == 1:
        from .gui import run_gui
        run_gui()
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

    assistant = Assistant(cfg, voice=voice)

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
