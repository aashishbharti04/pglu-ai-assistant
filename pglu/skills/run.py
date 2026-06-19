"""Run arbitrary system commands and report the REAL output or error (never a fake 'done').

Explicitly user-triggered with a prefix ('cmd', 'powershell', 'run command', …) so the AI never
executes commands on its own. This is powerful — see SECURITY.md."""

from __future__ import annotations

import subprocess

from .base import Skill


class Run(Skill):
    name = "run"
    priority = 18  # before app/web skills

    def intents(self):
        return [(r"^\s*(?:cmd|shell|powershell|terminal|exec(?:ute)?|run command)\s+(?P<cmd>.+)", self.run)]

    def examples(self):
        return ["cmd ipconfig", "powershell Get-Date", "run command dir"]

    def run(self, text, m):
        cmd = m.group("cmd").strip()
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            out = (r.stdout or "").strip()
            err = (r.stderr or "").strip()
            if r.returncode == 0:
                return out[:1500] if out else "✓ Done (the command ran with no output)."
            detail = (err or out or "no error message").strip()
            return f"⚠ It didn't work — exit code {r.returncode}:\n{detail[:1500]}"
        except subprocess.TimeoutExpired:
            return "⚠ That command took too long and timed out (30s limit)."
        except Exception as e:
            return f"⚠ I couldn't run that: {e}"
