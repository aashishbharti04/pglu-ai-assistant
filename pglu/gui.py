"""A simple desktop chat window for Pglu (Tkinter — ships with Python).

Launch with `pglu gui`, `python -m pglu gui`, or the desktop shortcut. Tkinter is imported
inside run_gui() so importing this module never fails on headless/CI environments.
"""

from __future__ import annotations

import os
import threading

from .config import Config
from .assistant import Assistant

ICON = os.path.join(os.path.dirname(__file__), "assets", "pglu.ico")

# dark palette
BG = "#0b0f17"
PANEL = "#131925"
BORDER = "#1e2a42"
TEXT = "#e8edf5"
MUTED = "#8a96aa"
USER = "#22d3ee"
NOVA = "#8b5cf6"

QUICK = ["what time is it", "weather in Delhi", "open notepad",
         "what is 24 times 7", "who is Alan Turing", "tell me a joke"]


def run_gui():
    import tkinter as tk
    from tkinter import scrolledtext

    cfg = Config.load()

    voice = None
    try:
        from .voice import Voice
        v = Voice(cfg)
        if v.available:
            voice = v
    except Exception:
        voice = None

    assistant = Assistant(cfg, voice=voice)

    root = tk.Tk()
    root.title(f"{cfg.name} AI Assistant")
    root.geometry("560x640")
    root.minsize(440, 520)
    root.configure(bg=BG)
    try:
        root.iconbitmap(ICON)
    except Exception:
        pass

    # ---- header ----
    header = tk.Frame(root, bg=BG)
    header.pack(fill="x", padx=16, pady=(14, 6))
    tk.Label(header, text="🤖 " + cfg.name, font=("Segoe UI", 16, "bold"),
             bg=BG, fg=USER).pack(side="left")
    status = tk.StringVar(value="online · ask me anything")
    tk.Label(header, textvariable=status, font=("Segoe UI", 9), bg=BG, fg=MUTED).pack(side="right")

    # ---- chat ----
    chat = scrolledtext.ScrolledText(root, wrap="word", bg=PANEL, fg=TEXT, bd=0,
                                     font=("Segoe UI", 11), padx=14, pady=12,
                                     insertbackground=TEXT, state="disabled",
                                     highlightthickness=1, highlightbackground=BORDER)
    chat.pack(fill="both", expand=True, padx=16, pady=6)
    chat.tag_config("user_name", foreground=USER, font=("Segoe UI", 10, "bold"))
    chat.tag_config("nova_name", foreground=NOVA, font=("Segoe UI", 10, "bold"))
    chat.tag_config("body", foreground=TEXT, font=("Segoe UI", 11))
    chat.tag_config("meta", foreground=MUTED, font=("Segoe UI", 9, "italic"))

    def append(who, text):
        chat.config(state="normal")
        chat.insert("end", ("You" if who == "user" else cfg.name) + "\n", who + "_name")
        chat.insert("end", text + "\n\n", "body")
        chat.see("end")
        chat.config(state="disabled")

    # ---- quick chips ----
    chips = tk.Frame(root, bg=BG)
    chips.pack(fill="x", padx=14)
    for q in QUICK:
        tk.Button(chips, text=q, font=("Segoe UI", 8), bg=PANEL, fg=MUTED,
                  activebackground=BORDER, activeforeground=TEXT, bd=0, padx=8, pady=3,
                  cursor="hand2", command=lambda t=q: submit(t)).pack(side="left", padx=3, pady=4)

    # ---- input row ----
    row = tk.Frame(root, bg=BG)
    row.pack(fill="x", padx=16, pady=(4, 14))
    entry = tk.Entry(row, font=("Segoe UI", 12), bg=PANEL, fg=TEXT, bd=0,
                     insertbackground=USER, highlightthickness=1, highlightbackground=BORDER,
                     highlightcolor=USER)
    entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))

    speak_var = tk.BooleanVar(value=bool(voice and voice.tts_ok))

    def styled_btn(parent, text, cmd, primary=False):
        return tk.Button(parent, text=text, command=cmd, cursor="hand2", bd=0,
                         font=("Segoe UI", 11, "bold"),
                         bg=(USER if primary else PANEL), fg=("#06121a" if primary else TEXT),
                         activebackground=(NOVA if primary else BORDER),
                         activeforeground=("#06121a" if primary else TEXT), padx=14, pady=6)

    if voice and voice.stt_ok:
        styled_btn(row, "🎙️", lambda: on_mic()).pack(side="left", padx=(0, 8))
    styled_btn(row, "Send", lambda: submit(entry.get()), primary=True).pack(side="left")

    if voice and voice.tts_ok:
        tk.Checkbutton(root, text="🔊 speak replies", variable=speak_var, bg=BG, fg=MUTED,
                       selectcolor=PANEL, activebackground=BG, activeforeground=TEXT,
                       font=("Segoe UI", 9)).pack(anchor="e", padx=18)

    # ---- behaviour ----
    def submit(text):
        text = (text or "").strip()
        if not text:
            return
        append("user", text)
        entry.delete(0, "end")
        if assistant.is_exit(text):
            status.set("bye 👋")
            root.after(500, root.destroy)
            return
        status.set("thinking…")
        threading.Thread(target=_work, args=(text,), daemon=True).start()

    def _work(text):
        reply = assistant.respond(text)
        root.after(0, lambda: _done(reply))

    def _done(reply):
        status.set("online · ask me anything")
        append("nova", reply)
        if speak_var.get() and voice:
            threading.Thread(target=lambda: voice.speak(reply), daemon=True).start()

    def on_mic():
        status.set("🎙️ listening…")

        def _listen():
            t = voice.listen()
            root.after(0, lambda: (status.set("online · ask me anything"), submit(t)) if t
                       else status.set("didn't catch that — try again or type"))
        threading.Thread(target=_listen, daemon=True).start()

    entry.bind("<Return>", lambda e: submit(entry.get()))
    append("nova", f"Hi {cfg.user_name}! I'm {cfg.name}. Ask me to open apps, search the web, "
                   "answer questions, check your system, set timers and more. Type 'help' to see everything.")
    entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    run_gui()
