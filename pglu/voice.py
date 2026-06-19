"""Voice I/O — optional, no PyAudio.
  • TTS via pyttsx3 (offline)
  • STT via SpeechRecognition (Google) over audio captured with sounddevice (prebuilt wheels)
Everything degrades gracefully so the assistant always works in text mode."""

from __future__ import annotations

from . import audio


def list_voices():
    """Return [(id, name), ...] of installed system TTS voices (empty if unavailable)."""
    try:
        import pyttsx3
        eng = pyttsx3.init()
        return [(v.id, v.name) for v in eng.getProperty("voices")]
    except Exception:
        return []


class Voice:
    def __init__(self, config):
        self.config = config
        self.tts = None
        self.tts_ok = False
        self.stt_ok = audio.stt_available()

        try:
            import pyttsx3
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", config.tts_rate)
            self.tts_ok = True
            if (config.tts_voice or "").strip():
                self.set_voice(config.tts_voice)
        except Exception:
            pass

    def set_voice(self, name):
        """Switch the speaking voice to the first installed voice matching `name`."""
        self.config.tts_voice = name or ""
        if not self.tts_ok:
            return
        pref = (name or "").strip().lower()
        if not pref:
            return
        try:
            for v in self.tts.getProperty("voices"):
                if pref in (v.name or "").lower() or pref in (v.id or "").lower():
                    self.tts.setProperty("voice", v.id)
                    return
        except Exception:
            pass

    @property
    def available(self):
        return self.tts_ok or self.stt_ok

    def speak(self, text):
        if not text or not self.tts_ok:
            return
        try:
            self.tts.say(text)
            self.tts.runAndWait()
        except Exception:
            pass  # caller also prints the text

    def listen(self):
        """Record a phrase from the mic and transcribe it. Returns text or None."""
        if not self.stt_ok:
            return None
        return audio.recognize(audio.record_phrase())
