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


def launch_detached(minimized=False):
    """Start the GUI as an independent process (survives closing the terminal)."""
    pyw = _pythonw()
    main_py = _target()
    args = [pyw] + ([main_py, "gui"] if main_py else ["-m", "pglu", "gui"])
    if minimized:
        args.append("min")
    kwargs = {}
    if platform.system() == "Windows":
        # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP — fully detach from the console
        kwargs["creationflags"] = 0x00000008 | 0x00000200
        kwargs["close_fds"] = True
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(args, **kwargs)


def _startup_dir():
    return os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows",
                        "Start Menu", "Programs", "Startup")


def install_autostart(minimized=True):
    """Launch Pglu automatically when the user logs in."""
    system = platform.system()
    pyw = _pythonw()
    main_py = _target()
    suffix = " gui min" if minimized else " gui"

    if system == "Windows":
        sd = _startup_dir()
        os.makedirs(sd, exist_ok=True)
        lnk = os.path.join(sd, "Pglu AI Assistant.lnk")
        if main_py:
            args = f'"{main_py}"{suffix}'
            workdir = os.path.dirname(main_py)
        else:
            args = f"-m pglu{suffix}"
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

    if system == "Linux":
        d = os.path.join(os.path.expanduser("~"), ".config", "autostart")
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, "pglu-ai-assistant.desktop")
        exec_line = (f'{pyw} "{main_py}"{suffix}') if main_py else (f"{pyw} -m pglu{suffix}")
        with open(path, "w", encoding="utf-8") as f:
            f.write("[Desktop Entry]\nType=Application\nName=Pglu AI Assistant\n"
                    f"Exec={exec_line}\nIcon={ICON}\nTerminal=false\nX-GNOME-Autostart-enabled=true\n")
        return path

    return None  # macOS: add Pglu via System Settings → General → Login Items


def remove_autostart():
    system = platform.system()
    if system == "Windows":
        p = os.path.join(_startup_dir(), "Pglu AI Assistant.lnk")
    elif system == "Linux":
        p = os.path.join(os.path.expanduser("~"), ".config", "autostart", "pglu-ai-assistant.desktop")
    else:
        return None
    if os.path.exists(p):
        os.remove(p)
        return p
    return None
