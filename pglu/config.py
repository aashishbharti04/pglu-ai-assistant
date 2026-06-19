"""User configuration, persisted to ~/.pglu/config.json."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".pglu")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def _ensure_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)


@dataclass
class Config:
    name: str = "Pglu"
    user_name: str = "boss"
    wake_word: str = "pglu"
    tts_rate: int = 175
    voice_enabled: bool = False
    default_city: str = ""
    # "Jarvis mode" wake triggers (work while the window is minimized / screen off, PC awake)
    wake_hotkey_enabled: bool = False
    wake_hotkey: str = "<ctrl>+<alt>+p"
    wake_clap_enabled: bool = False
    clap_threshold: float = 0.45
    wake_word_enabled: bool = False
    # AI brain + personality
    user_about: str = ""
    persona: str = "jarvis"
    custom_persona: str = ""
    ai_provider: str = "auto"   # auto | ollama | openai | anthropic | gemini | groq | openrouter | none
    ai_model: str = ""
    ai_api_key: str = ""
    memory_enabled: bool = True  # remember conversations across sessions
    tts_voice: str = ""          # preferred system voice (name substring); blank = default

    @classmethod
    def load(cls) -> "Config":
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
            return cls(**known)
        except Exception:
            return cls()

    def save(self) -> None:
        _ensure_dir()
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)


def data_path(filename: str) -> str:
    """Path for skill data files (notes, etc.)."""
    _ensure_dir()
    return os.path.join(CONFIG_DIR, filename)
