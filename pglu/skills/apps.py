"""Apps: launch native desktop applications (true PC control).

Known cross-platform apps launch instantly; anything else is found by searching the
Start Menu / Desktop shortcuts (Windows), so "open <any installed app>" actually works."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess

from .base import Skill

# fast, cross-platform built-ins
_APPS = {
    "notepad": {"Windows": "notepad", "Darwin": "TextEdit", "Linux": "gedit"},
    "calculator": {"Windows": "calc", "Darwin": "Calculator", "Linux": "gnome-calculator"},
    "calc": {"Windows": "calc", "Darwin": "Calculator", "Linux": "gnome-calculator"},
    "paint": {"Windows": "mspaint", "Darwin": "", "Linux": ""},
    "file explorer": {"Windows": "explorer", "Darwin": "Finder", "Linux": "xdg-open ."},
    "explorer": {"Windows": "explorer", "Darwin": "Finder", "Linux": "xdg-open ."},
    "files": {"Windows": "explorer", "Darwin": "Finder", "Linux": "xdg-open ."},
    "command prompt": {"Windows": "cmd", "Darwin": "Terminal", "Linux": "x-terminal-emulator"},
    "terminal": {"Windows": "cmd", "Darwin": "Terminal", "Linux": "x-terminal-emulator"},
    "settings": {"Windows": "start ms-settings:", "Darwin": "System Settings", "Linux": "gnome-control-center"},
    "camera": {"Windows": "start microsoft.windows.camera:", "Darwin": "Photo Booth", "Linux": "cheese"},
    "task manager": {"Windows": "taskmgr", "Darwin": "Activity Monitor", "Linux": "gnome-system-monitor"},
}

_INDEX = None       # cached {shortcut_name_lower: path}
_START_APPS = None  # cached [(name_lower, AppID), ...] from Get-StartApps (Windows, incl. Store apps)


def _best(pairs, query):
    """From [(name_lower, value)] pick the closest match to query, or None."""
    q = " ".join(query.lower().split())
    toks = q.split()
    for nm, val in pairs:
        if nm == q:
            return val
    cands = [(nm, val) for nm, val in pairs if all(t in nm for t in toks)]
    if cands:
        cands.sort(key=lambda x: len(x[0]))   # shortest (closest) name
        return cands[0][1]
    return None


def _start_apps():
    """All Start-menu apps incl. UWP/Store (Windows) via Get-StartApps → [(name_lower, AppID)]."""
    global _START_APPS
    if _START_APPS is not None:
        return _START_APPS
    _START_APPS = []
    if platform.system() != "Windows":
        return _START_APPS
    try:
        import json
        out = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                              "Get-StartApps | ConvertTo-Json -Compress"],
                             capture_output=True, text=True, timeout=20)
        data = json.loads(out.stdout or "[]")
        if isinstance(data, dict):
            data = [data]
        _START_APPS = [(d.get("Name", "").lower(), d.get("AppID", "")) for d in data if d.get("AppID")]
    except Exception:
        _START_APPS = []
    return _START_APPS


def _scan_dirs():
    env = os.environ.get
    dirs = [
        os.path.join(env("PROGRAMDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join(env("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(env("PUBLIC", ""), "Desktop"),
        os.path.join(env("APPDATA", ""), "Microsoft", "Internet Explorer", "Quick Launch", "User Pinned", "TaskBar"),
    ]
    return [d for d in dirs if d and os.path.isdir(d)]


def _shortcut_index():
    global _INDEX
    if _INDEX is not None:
        return _INDEX
    _INDEX = {}
    exts = (".lnk", ".url", ".appref-ms")
    try:
        for d in _scan_dirs():
            for root, _dirs, files in os.walk(d):
                for f in files:
                    if f.lower().endswith(exts):
                        stem = os.path.splitext(f)[0].lower()
                        _INDEX.setdefault(stem, os.path.join(root, f))
    except Exception:
        pass
    return _INDEX


def _find_app(name):
    """Return ('appsfolder', AppID) | ('path', shortcut_path) | None."""
    aid = _best(_start_apps(), name)          # 1) Start apps (covers Store apps like Claude)
    if aid:
        return ("appsfolder", aid)
    p = _best(list(_shortcut_index().items()), name)   # 2) shortcut files
    if p:
        return ("path", p)
    return None


class Apps(Skill):
    name = "apps"
    priority = 25  # before Web's generic "open ..."

    def intents(self):
        return [(r"\b(?:open|launch|start|run)\s+(?P<app>.+)", self.open_app)]

    def examples(self):
        return ["open notepad", "open calculator", "open chrome", "launch task manager", "open <any app>"]

    def open_app(self, text, m):
        raw = m.group("app").strip()
        app = " ".join(raw.lower().split())

        # 1) fast built-ins
        spec = _APPS.get(app)
        if spec:
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

        # 2) any installed app (Start apps incl. Store, then Start Menu / Desktop shortcuts)
        found = _find_app(app)
        if found:
            kind, val = found
            try:
                if kind == "appsfolder":
                    subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{val}"])
                elif platform.system() == "Windows":
                    os.startfile(val)  # launches a shortcut the user already has
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", val])
                else:
                    subprocess.Popen(["xdg-open", val])
                label = raw if kind == "appsfolder" else os.path.splitext(os.path.basename(val))[0]
                return f"Opening {label}."
            except Exception as e:
                return f"I found {raw} but couldn't launch it: {e}"

        # 3) not an app → let the Web skill try (it may be a website) or report honestly
        return None
