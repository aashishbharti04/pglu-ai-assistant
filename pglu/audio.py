"""Microphone capture via sounddevice (prebuilt wheels — no PyAudio, no C compiler).

Records a phrase with simple voice-activity detection and hands raw PCM to SpeechRecognition.
All imports are lazy so importing this module never fails when the deps are absent.
"""

from __future__ import annotations

SAMPLE_RATE = 16000


def available() -> bool:
    try:
        import numpy  # noqa: F401
        import sounddevice  # noqa: F401
        return True
    except Exception:
        return False


def record_phrase(max_seconds: float = 8.0, silence_seconds: float = 1.0,
                  threshold: float = 0.02, start_timeout: float = 3.0):
    """Record from the default mic until ~silence after speech (or max_seconds).
    Returns raw 16-bit mono PCM bytes, or None on failure / no speech."""
    try:
        import numpy as np
        import sounddevice as sd
    except Exception:
        return None
    chunk = int(SAMPLE_RATE * 0.1)  # 100 ms blocks
    buf, total, silence, voiced = [], 0.0, 0.0, False
    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16") as stream:
            while total < max_seconds:
                data, _ = stream.read(chunk)
                buf.append(bytes(data))
                total += 0.1
                amp = float(np.abs(np.frombuffer(bytes(data), dtype="int16")).mean()) / 32768.0
                if amp > threshold:
                    voiced, silence = True, 0.0
                elif voiced:
                    silence += 0.1
                    if silence >= silence_seconds:
                        break
                elif total >= start_timeout:
                    return None  # nobody spoke
    except Exception:
        return None
    return b"".join(buf) if voiced else None


def recognize(raw: bytes):
    """Transcribe raw 16-bit mono 16kHz PCM via Google (free). Returns text or None."""
    if not raw:
        return None
    try:
        import speech_recognition as sr
        audio = sr.AudioData(raw, SAMPLE_RATE, 2)
        return sr.Recognizer().recognize_google(audio)
    except Exception:
        return None


def stt_available() -> bool:
    try:
        import speech_recognition  # noqa: F401
        return available()
    except Exception:
        return False
