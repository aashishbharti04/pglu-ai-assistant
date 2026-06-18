"""Voice I/O — optional. STT via SpeechRecognition (Google), TTS via pyttsx3.
Everything degrades gracefully so the assistant always works in text mode."""

from __future__ import annotations


class Voice:
    def __init__(self, config):
        self.config = config
        self.tts = None
        self.sr = None
        self.recognizer = None
        self.tts_ok = False
        self.stt_ok = False

        try:
            import pyttsx3
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", config.tts_rate)
            self.tts_ok = True
        except Exception:
            pass

        try:
            import speech_recognition as sr
            self.sr = sr
            self.recognizer = sr.Recognizer()
            # constructing Microphone needs PyAudio; probe it
            sr.Microphone()
            self.stt_ok = True
        except Exception:
            pass

    @property
    def available(self):
        return self.tts_ok or self.stt_ok

    def speak(self, text):
        if not text:
            return
        if self.tts_ok:
            try:
                self.tts.say(text)
                self.tts.runAndWait()
                return
            except Exception:
                pass
        # silent fallback — caller also prints text

    def listen(self):
        """Return recognized text, or None on failure/unsupported."""
        if not self.stt_ok:
            return None
        try:
            with self.sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=9)
            return self.recognizer.recognize_google(audio)
        except Exception:
            return None
