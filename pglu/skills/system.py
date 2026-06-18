"""System: machine info, battery, CPU, RAM, disk, IP. Uses psutil if available."""

from __future__ import annotations

import platform
import shutil
import socket

from .base import Skill
from ..util import get_json

try:
    import psutil  # optional
    _PSUTIL = True
except Exception:
    _PSUTIL = False


def _need_psutil():
    return "That needs the optional 'psutil' package — run: pip install \"pglu-ai-assistant[system]\""


class System(Skill):
    name = "system"
    priority = 20

    def intents(self):
        return [
            (r"\bbattery\b|\bpower level\b", self.battery),
            (r"\bcpu\b|\bprocessor (?:usage|load)\b", self.cpu),
            (r"\b(?:ram|memory)\b", self.memory),
            (r"\b(?:disk|storage|space)\b", self.disk),
            (r"\b(?:ip address|my ip|what'?s my ip)\b", self.ip),
            (r"\b(?:system info|system information|specs|about this (?:pc|computer|system))\b", self.info),
        ]

    def examples(self):
        return ["battery", "cpu usage", "how much ram", "disk space", "my ip", "system info"]

    def battery(self, text, m):
        if not _PSUTIL:
            return _need_psutil()
        b = psutil.sensors_battery()
        if not b:
            return "No battery detected (desktop?)."
        plug = "charging" if b.power_plugged else "on battery"
        return f"Battery is at {round(b.percent)}% ({plug})."

    def cpu(self, text, m):
        if not _PSUTIL:
            return _need_psutil()
        return f"CPU usage is {psutil.cpu_percent(interval=0.5)}% across {psutil.cpu_count()} cores."

    def memory(self, text, m):
        if not _PSUTIL:
            return _need_psutil()
        v = psutil.virtual_memory()
        return f"RAM: {v.used / 1e9:.1f} GB used of {v.total / 1e9:.1f} GB ({v.percent}%)."

    def disk(self, text, m):
        total, used, free = shutil.disk_usage("/" if platform.system() != "Windows" else "C:\\")
        return f"Disk: {used / 1e9:.0f} GB used of {total / 1e9:.0f} GB ({free / 1e9:.0f} GB free)."

    def ip(self, text, m):
        local = socket.gethostbyname(socket.gethostname())
        try:
            pub = get_json("https://api.ipify.org?format=json").get("ip", "?")
        except Exception:
            pub = "unavailable"
        return f"Local IP: {local} · Public IP: {pub}"

    def info(self, text, m):
        u = platform.uname()
        return f"{u.system} {u.release} on {u.machine}. Host: {u.node}. Python {platform.python_version()}."
