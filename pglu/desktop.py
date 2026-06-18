"""Create a clickable desktop shortcut that opens the Pglu GUI (no terminal window)."""

from __future__ import annotations

import os
import platform
import subprocess
import sys

ICON = os.path.join(os.path.dirname(__file__), "assets", "pglu.ico")


def _pythonw() -> str:
    """A GUI Python interpreter (no console window on Windows)."""
    exe = sys.executable
    if platform.system() == "Windows":
        cand = exe.replace("python.exe", "pythonw.exe")
        if os.path.exists(cand):
            return cand
    return exe


def _target():
    """Prefer the cloned repo's main.py (works without pip install); else 'python -m pglu'."""
    repo_main = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
    if os.path.exists(repo_main):
        return repo_main
    return None


def _desktop_dir() -> str:
    d = os.path.join(os.path.expanduser("~"), "Desktop")
    return d if os.path.isdir(d) else os.path.expanduser("~")


def install_shortcut() -> str:
    system = platform.system()
    pyw = _pythonw()
    main_py = _target()
    desktop = _desktop_dir()

    if system == "Windows":
        lnk = os.path.join(desktop, "Pglu AI Assistant.lnk")
        if main_py:
            args = f'"{main_py}" gui'
            workdir = os.path.dirname(main_py)
        else:
            args = "-m pglu gui"
            workdir = os.path.expanduser("~")
        ps = (
            "$W=New-Object -ComObject WScript.Shell;"
            f'$S=$W.CreateShortcut("{lnk}");'
            f'$S.TargetPath="{pyw}";'
            f"$S.Arguments='{args}';"
            f'$S.WorkingDirectory="{workdir}";'
            f'$S.IconLocation="{ICON}";'
            '$S.Description="Pglu AI Assistant";'
            "$S.Save()"
        )
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], check=True)
        return lnk

    if system == "Darwin":
        cmd = os.path.join(desktop, "Pglu AI Assistant.command")
        run = f'"{pyw}" "{main_py}" gui' if main_py else f'"{pyw}" -m pglu gui'
        with open(cmd, "w", encoding="utf-8") as f:
            f.write("#!/bin/bash\n" + run + "\n")
        os.chmod(cmd, 0o755)
        return cmd

    # Linux: a .desktop launcher
    path = os.path.join(desktop, "pglu-ai-assistant.desktop")
    exec_line = f'{pyw} "{main_py}" gui' if main_py else f"{pyw} -m pglu gui"
    content = (
        "[Desktop Entry]\nType=Application\nName=Pglu AI Assistant\n"
        f"Exec={exec_line}\nIcon={ICON}\nTerminal=false\nCategories=Utility;\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    os.chmod(path, 0o755)
    return path
