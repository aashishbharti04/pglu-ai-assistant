"""A desktop chat window for Pglu (Tkinter — ships with Python), with optional
'Jarvis mode' wake triggers. Tkinter is imported inside run_gui() so importing this
module never fails on headless/CI environments.
"""

from __future__ import annotations

import os
import threading

from .config import Config
from .assistant import Assistant

ICON = os.path.join(os.path.dirname(__file__), "assets", "pglu.ico")

BG = "#0b0f17"; PANEL = "#131925"; BORDER = "#1e2a42"
TEXT = "#e8edf5"; MUTED = "#8a96aa"; USER = "#22d3ee"; NOVA = "#8b5cf6"

QUICK = ["what time is it", "weather in Delhi", "open notepad",
         "what is 24 times 7", "who is Alan Turing", "tell me a joke"]


def run_gui():
    import tkinter as tk
    from tkinter import scrolledtext
    from .wake import WakeListener, hotkey_available, clap_available, word_available

    cfg = Config.load()

    voice = None
    try:
        from .voice import Voice
        v = Voice(cfg)
        if v.available:
            voice = v
    except Exception:
        voice = None

    from .ai import Brain
    from .persona import persona_list
    assistant = Assistant(cfg, voice=voice, brain=Brain(cfg))

    root = tk.Tk()
    root.title(f"{cfg.name} AI Assistant")
    root.geometry("560x660")
    root.minsize(440, 540)
    root.configure(bg=BG)
    try:
        root.iconbitmap(ICON)
    except Exception:
        pass

    # ---- header ----
    header = tk.Frame(root, bg=BG)
    header.pack(fill="x", padx=16, pady=(14, 6))
    tk.Label(header, text="🤖 " + cfg.name, font=("Segoe UI", 16, "bold"), bg=BG, fg=USER).pack(side="left")
    tk.Button(header, text="⚙", font=("Segoe UI", 13), bg=BG, fg=MUTED, bd=0, cursor="hand2",
              activebackground=BG, activeforeground=TEXT, command=lambda: open_settings()).pack(side="right")
    status = tk.StringVar(value="online · ask me anything")
    tk.Label(header, textvariable=status, font=("Segoe UI", 9), bg=BG, fg=MUTED).pack(side="right", padx=8)

    # ---- chat ----
    chat = scrolledtext.ScrolledText(root, wrap="word", bg=PANEL, fg=TEXT, bd=0, font=("Segoe UI", 11),
                                     padx=14, pady=12, insertbackground=TEXT, state="disabled",
                                     highlightthickness=1, highlightbackground=BORDER)
    chat.pack(fill="both", expand=True, padx=16, pady=6)
    chat.tag_config("user_name", foreground=USER, font=("Segoe UI", 10, "bold"))
    chat.tag_config("nova_name", foreground=NOVA, font=("Segoe UI", 10, "bold"))
    chat.tag_config("body", foreground=TEXT, font=("Segoe UI", 11))

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
        tk.Button(chips, text=q, font=("Segoe UI", 8), bg=PANEL, fg=MUTED, activebackground=BORDER,
                  activeforeground=TEXT, bd=0, padx=8, pady=3, cursor="hand2",
                  command=lambda t=q: submit(t)).pack(side="left", padx=3, pady=4)

    # ---- input row ----
    row = tk.Frame(root, bg=BG)
    row.pack(fill="x", padx=16, pady=(4, 12))
    entry = tk.Entry(row, font=("Segoe UI", 12), bg=PANEL, fg=TEXT, bd=0, insertbackground=USER,
                     highlightthickness=1, highlightbackground=BORDER, highlightcolor=USER)
    entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
    speak_var = tk.BooleanVar(value=bool(voice and voice.tts_ok))

    def styled_btn(parent, text, cmd, primary=False):
        return tk.Button(parent, text=text, command=cmd, cursor="hand2", bd=0, font=("Segoe UI", 11, "bold"),
                         bg=(USER if primary else PANEL), fg=("#06121a" if primary else TEXT),
                         activebackground=(NOVA if primary else BORDER),
                         activeforeground=("#06121a" if primary else TEXT), padx=14, pady=6)

    if voice and voice.stt_ok:
        styled_btn(row, "🎙️", lambda: on_mic()).pack(side="left", padx=(0, 8))
    styled_btn(row, "Send", lambda: submit(entry.get()), primary=True).pack(side="left")

    # ---- behaviour ----
    def submit(text):
        text = (text or "").strip()
        if not text:
            return
        append("user", text)
        entry.delete(0, "end")
        if assistant.is_exit(text):
            status.set("bye 👋")
            root.after(400, _quit)
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
        if not (voice and voice.stt_ok):
            append("nova", "Voice input needs the mic extra: pip install \"pglu-ai-assistant[mic]\"")
            return
        status.set("🎙️ listening…")

        def _listen():
            t = voice.listen()
            root.after(0, lambda: (status.set("online · ask me anything"), submit(t)) if t
                       else status.set("didn't catch that — try again or type"))
        threading.Thread(target=_listen, daemon=True).start()

    entry.bind("<Return>", lambda e: submit(entry.get()))

    # ---- wake / Jarvis mode ----
    def _wake_ui(source):
        try:
            root.deiconify(); root.lift(); root.focus_force()
            root.attributes("-topmost", True)
            root.after(400, lambda: root.attributes("-topmost", False))
        except Exception:
            pass
        status.set(f"⚡ woke via {source}")
        if voice and voice.tts_ok and speak_var.get():
            threading.Thread(target=lambda: voice.speak("Yes?"), daemon=True).start()
        if voice and voice.stt_ok:
            on_mic()
        else:
            entry.focus_set()

    wake = {"listener": None}

    def restart_wake():
        if wake["listener"]:
            wake["listener"].stop()
        wl = WakeListener(cfg, on_wake=lambda src: root.after(0, lambda: _wake_ui(src)))
        wake["listener"] = wl
        if wl.any_enabled():
            wl.start()

    # ---- settings dialog ----
    def open_settings():
        win = tk.Toplevel(root, bg=BG)
        win.title("Settings")
        win.geometry("460x760")
        win.configure(bg=BG)
        try:
            win.iconbitmap(ICON)
        except Exception:
            pass
        win.transient(root)

        def hdr(t):
            tk.Label(win, text=t, bg=BG, fg=USER, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=18, pady=(14, 2))

        def hint(t):
            tk.Label(win, text=t, bg=BG, fg=MUTED, font=("Segoe UI", 8), wraplength=380, justify="left").pack(anchor="w", padx=34)

        def chk(parent, text, var, enabled=True):
            c = tk.Checkbutton(parent, text=text, variable=var, bg=BG, fg=TEXT, selectcolor=PANEL,
                               activebackground=BG, activeforeground=TEXT, font=("Segoe UI", 10),
                               anchor="w")
            if not enabled:
                c.config(state="disabled", fg=MUTED)
            c.pack(anchor="w", padx=18, pady=2, fill="x")
            return c

        def field_row(label, value, mask=False):
            r = tk.Frame(win, bg=BG)
            r.pack(fill="x", padx=18, pady=2)
            tk.Label(r, text=label, bg=BG, fg=MUTED, font=("Segoe UI", 9), width=11, anchor="w").pack(side="left")
            e = tk.Entry(r, bg=PANEL, fg=TEXT, bd=0, insertbackground=USER, font=("Segoe UI", 10),
                         highlightthickness=1, highlightbackground=BORDER)
            if mask:
                e.config(show="•")
            e.insert(0, value or "")
            e.pack(side="left", fill="x", expand=True, ipady=3)
            return e

        hdr("🧠 AI brain & persona")
        ai_name = field_row("AI name", cfg.name)
        your_name = field_row("Your name", cfg.user_name)
        about = field_row("About you", cfg.user_about)
        prow = tk.Frame(win, bg=BG); prow.pack(fill="x", padx=18, pady=2)
        tk.Label(prow, text="Personality", bg=BG, fg=MUTED, font=("Segoe UI", 9), width=11, anchor="w").pack(side="left")
        persona_var = tk.StringVar(value=cfg.persona)
        om = tk.OptionMenu(prow, persona_var, *[pid for pid, _ in persona_list()])
        om.config(bg=PANEL, fg=TEXT, bd=0, highlightthickness=1, highlightbackground=BORDER,
                  activebackground=BORDER, font=("Segoe UI", 9))
        om["menu"].config(bg=PANEL, fg=TEXT)
        om.pack(side="left", fill="x", expand=True)
        custom = field_row("Custom style", cfg.custom_persona)
        provider = field_row("Provider", cfg.ai_provider)
        model = field_row("Model", cfg.ai_model)
        apikey = field_row("API key", cfg.ai_api_key, mask=True)
        hint("Provider: ollama (local, free) · openai · anthropic · gemini · groq · none. "
             "Local AI: install Ollama + `ollama pull llama3.2`. Keys are stored locally.")

        hdr("Voice")
        spk = tk.BooleanVar(value=speak_var.get())
        chk(win, "🔊 Speak replies out loud", spk, enabled=bool(voice and voice.tts_ok))
        if not (voice and voice.tts_ok):
            hint('Install voice output:  pip install "pglu-ai-assistant[voice]"')

        hdr("⚡ Jarvis wake mode")
        hint("Wake Pglu while the window is minimized (PC awake). Choose any triggers:")

        hk = tk.BooleanVar(value=cfg.wake_hotkey_enabled)
        chk(win, "⌨  Global hotkey", hk, enabled=hotkey_available())
        hkrow = tk.Frame(win, bg=BG); hkrow.pack(fill="x", padx=34)
        tk.Label(hkrow, text="combo:", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(side="left")
        hk_entry = tk.Entry(hkrow, bg=PANEL, fg=TEXT, bd=0, font=("Consolas", 10), insertbackground=USER,
                            highlightthickness=1, highlightbackground=BORDER)
        hk_entry.insert(0, cfg.wake_hotkey); hk_entry.pack(side="left", fill="x", expand=True, padx=6, ipady=3)
        if not hotkey_available():
            hint('Install:  pip install "pglu-ai-assistant[wake]"')

        cl = tk.BooleanVar(value=cfg.wake_clap_enabled)
        chk(win, "👏  Double-clap", cl, enabled=clap_available())
        clrow = tk.Frame(win, bg=BG); clrow.pack(fill="x", padx=34)
        tk.Label(clrow, text="sensitivity:", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(side="left")
        cl_scale = tk.Scale(clrow, from_=0.8, to=0.15, resolution=0.05, orient="horizontal", bg=BG,
                            fg=TEXT, troughcolor=PANEL, highlightthickness=0, bd=0, length=180, showvalue=True)
        cl_scale.set(cfg.clap_threshold); cl_scale.pack(side="left", padx=6)
        if not clap_available():
            hint('Install:  pip install "pglu-ai-assistant[clap]"')

        wd = tk.BooleanVar(value=cfg.wake_word_enabled)
        chk(win, "🗣  Wake word", wd, enabled=word_available())
        wdrow = tk.Frame(win, bg=BG); wdrow.pack(fill="x", padx=34)
        tk.Label(wdrow, text="word:", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(side="left")
        wd_entry = tk.Entry(wdrow, bg=PANEL, fg=TEXT, bd=0, font=("Segoe UI", 10), insertbackground=USER,
                            highlightthickness=1, highlightbackground=BORDER)
        wd_entry.insert(0, cfg.wake_word); wd_entry.pack(side="left", fill="x", expand=True, padx=6, ipady=3)
        if not word_available():
            hint('Needs mic + voice:  pip install "pglu-ai-assistant[voice]" and [mic]')

        def save():
            speak_var.set(spk.get())
            cfg.name = ai_name.get().strip() or cfg.name
            cfg.user_name = your_name.get().strip()
            cfg.user_about = about.get().strip()
            cfg.persona = persona_var.get()
            cfg.custom_persona = custom.get().strip()
            from .ai import normalize_provider
            cfg.ai_provider = normalize_provider(provider.get())
            cfg.ai_model = model.get().strip()
            cfg.ai_api_key = apikey.get().strip()
            cfg.wake_hotkey_enabled = hk.get(); cfg.wake_hotkey = hk_entry.get().strip() or "<ctrl>+<alt>+p"
            cfg.wake_clap_enabled = cl.get(); cfg.clap_threshold = float(cl_scale.get())
            cfg.wake_word_enabled = wd.get(); cfg.wake_word = wd_entry.get().strip() or "pglu"
            cfg.save()
            assistant.brain = Brain(cfg)   # pick up new provider / key / model
            restart_wake()
            status.set("⚡ Jarvis mode on" if wake["listener"] and wake["listener"].any_enabled() else "online · ask me anything")
            win.destroy()

        tk.Button(win, text="Save", command=save, bg=USER, fg="#06121a", bd=0, cursor="hand2",
                  font=("Segoe UI", 11, "bold"), padx=18, pady=6).pack(side="bottom", pady=16)

    def _quit():
        try:
            if wake["listener"]:
                wake["listener"].stop()
        except Exception:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", _quit)

    # greet + boot
    append("nova", f"Hi {cfg.user_name}! I'm {cfg.name}. Ask me to open apps, search the web, answer "
                   "questions, check your system, set timers and more. Type 'help', or click ⚙ to set up "
                   "hands-free wake (hotkey / clap / wake-word).")
    restart_wake()
    if wake["listener"] and wake["listener"].any_enabled():
        status.set("⚡ Jarvis mode on · ask me anything")
    entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    run_gui()
