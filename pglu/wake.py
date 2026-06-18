"""'Jarvis mode' wake triggers — wake Pglu while the window is minimized (PC awake).

Three optional backends, each with wheel-installable deps and graceful fallback:
  • hotkey  — a global keyboard shortcut         (pip install "pglu-ai-assistant[wake]")
  • clap    — double-clap detection via the mic  (pip install "pglu-ai-assistant[clap]")
  • word    — a spoken wake word                 (needs [voice] + [mic])
All imports are lazy, so importing this module never fails if the deps are absent.
"""

from __future__ import annotations

import threading
import time


def _has(mod: str) -> bool:
    try:
        __import__(mod)
        return True
    except Exception:
        return False


def hotkey_available() -> bool:
    return _has("pynput")


def clap_available() -> bool:
    return _has("sounddevice") and _has("numpy")


def word_available() -> bool:
    from . import audio
    return audio.stt_available()


class WakeListener:
    """Runs the enabled wake backends; calls on_wake(source) when triggered."""

    def __init__(self, config, on_wake):
        self.cfg = config
        self.on_wake = on_wake
        self._stop = threading.Event()
        self._hotkey = None
        self._threads = []

    def any_enabled(self) -> bool:
        return bool(self.cfg.wake_hotkey_enabled or self.cfg.wake_clap_enabled or self.cfg.wake_word_enabled)

    def start(self):
        self._stop.clear()
        if self.cfg.wake_hotkey_enabled and hotkey_available():
            self._start_hotkey()
        if self.cfg.wake_clap_enabled and clap_available():
            self._spawn(self._clap_loop)
        if self.cfg.wake_word_enabled and word_available():
            self._spawn(self._word_loop)

    def stop(self):
        self._stop.set()
        if self._hotkey is not None:
            try:
                self._hotkey.stop()
            except Exception:
                pass
            self._hotkey = None
        self._threads = []

    # ---- internals ----
    def _spawn(self, fn):
        t = threading.Thread(target=fn, daemon=True)
        t.start()
        self._threads.append(t)

    def _fire(self, source):
        try:
            self.on_wake(source)
        except Exception:
            pass

    def _start_hotkey(self):
        try:
            from pynput import keyboard
            combo = self.cfg.wake_hotkey or "<ctrl>+<alt>+p"
            self._hotkey = keyboard.GlobalHotKeys({combo: lambda: self._fire("hotkey")})
            self._hotkey.start()
        except Exception:
            self._hotkey = None

    def _clap_loop(self):
        try:
            import numpy as np
            import sounddevice as sd
        except Exception:
            return
        thr = max(0.08, float(self.cfg.clap_threshold or 0.45))
        last = [0.0]

        def cb(indata, frames, t, status):
            if self._stop.is_set():
                raise sd.CallbackStop()
            peak = float(np.abs(indata).max())
            if peak > thr:
                now = time.time()
                if 0.08 < now - last[0] < 0.6:   # two sharp peaks close together = a double clap
                    last[0] = 0.0
                    self._fire("clap")
                else:
                    last[0] = now

        try:
            with sd.InputStream(channels=1, samplerate=16000, blocksize=1024, callback=cb):
                while not self._stop.is_set():
                    time.sleep(0.1)
        except Exception:
            pass

    def _word_loop(self):
        from . import audio
        word = (self.cfg.wake_word or "pglu").lower()
        while not self._stop.is_set():
            try:
                raw = audio.record_phrase(max_seconds=4, silence_seconds=0.6, start_timeout=4)
                text = audio.recognize(raw) if raw else None
                if text and word in text.lower():
                    self._fire("word")
            except Exception:
                continue
