"""Apps: launch native desktop applications (true PC control)."""

from __future__ import annotations

import platform
import shutil
import subprocess

from .base import Skill

# canonical name -> {os: command}
_APPS = {
    "notepad": {"Windows": "notepad", "Darwin": "TextEdit", "Linux": "gedit"},
    "calculator": {"Windows": "calc", "Darwin": "Calculator", "Linux": "gnome-calculator"},
    "paint": {"Windows": "mspaint", "Darwin": "", "Linux": ""},
    "file explorer": {"Windows": "explorer", "Darwin": "Finder", "Linux": "xdg-open ."},
    "explorer": {"Windows": "explorer", "Darwin": "Finder", "Linux": "xdg-open ."},
    "command prompt": {"Windows": "cmd", "Darwin": "Terminal", "Linux": "x-terminal-emulator"},
    "terminal": {"Windows": "cmd", "Darwin": "Terminal", "Linux": "x-terminal-emulator"},
    "settings": {"Windows": "start ms-settings:", "Darwin": "System Settings", "Linux": "gnome-control-center"},
    "camera": {"Windows": "start microsoft.windows.camera:", "Darwin": "Photo Booth", "Linux": "cheese"},
    "task manager": {"Windows": "taskmgr", "Darwin": "Activity Monitor", "Linux": "gnome-system-monitor"},
    "browser": {"Windows": "start http://", "Darwin": "Safari", "Linux": "xdg-open http://"},
    "chrome": {"Windows": "start chrome", "Darwin": "Google Chrome", "Linux": "google-chrome"},
    "vscode": {"Windows": "code", "Darwin": "Visual Studio Code", "Linux": "code"},
    "code": {"Windows": "code", "Darwin": "Visual Studio Code", "Linux": "code"},
    "word": {"Windows": "start winword", "Darwin": "Microsoft Word", "Linux": ""},
    "excel": {"Windows": "start excel", "Darwin": "Microsoft Excel", "Linux": ""},
}


class Apps(Skill):
    name = "apps"
    priority = 25  # before Web's generic "open ..."

    def intents(self):
        names = "|".join(sorted((k.replace(" ", r"\s+") for k in _APPS), key=len, reverse=True))
        return [(r"\b(?:open|launch|start)\s+(?P<app>" + names + r")\b", self.open_app)]

    def examples(self):
        return ["open notepad", "open calculator", "launch task manager", "open settings"]

    def open_app(self, text, m):
        app = " ".join(m.group("app").lower().split())
        spec = _APPS.get(app)
        if not spec:
            return None
        cmd = spec.get(platform.system(), "")
        if not cmd:
            return f"Sorry, I don't know how to open {app} on this system."
        try:
            if platform.system() == "Darwin":
                subprocess.Popen(["open", "-a", cmd])
            elif cmd.startswith("start ") or cmd.endswith(":"):
                subprocess.Popen(cmd, shell=True)
            elif shutil.which(cmd) or platform.system() == "Windows":
                subprocess.Popen(cmd, shell=(platform.system() == "Windows"))
            else:
                subprocess.Popen([cmd])
            return f"Opening {app}."
        except Exception as e:
            return f"I couldn't open {app}: {e}"
