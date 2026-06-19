"""Offline tests for Pglu's core — no network, no audio."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pglu.util import safe_math  # noqa: E402
from pglu.config import Config  # noqa: E402
from pglu.assistant import Assistant  # noqa: E402
from pglu.persona import build_system_prompt  # noqa: E402


def make():
    return Assistant(Config())


def test_safe_math():
    assert safe_math("2 + 2") == 4
    assert safe_math("25 times 4") == 100
    assert safe_math("100 divided by 4") == 25
    assert safe_math("2 to the power 10") == 1024
    assert safe_math("not math") is None


def test_respond_math():
    assert "100" in make().respond("what is 25 times 4")


def test_respond_time_and_date():
    a = make()
    assert "It's" in a.respond("what time is it")
    assert "Today is" in a.respond("what's the date")


def test_respond_fun():
    a = make()
    assert a.respond("flip a coin")
    assert "between" in a.respond("random number between 1 and 5")
    assert len(a.respond("generate a password 16")) >= 16


def test_notes_roundtrip(tmp_path, monkeypatch):
    # isolate notes file
    import pglu.skills.productivity as prod
    f = tmp_path / "notes.json"
    monkeypatch.setattr(prod, "NOTES_FILE", str(f))
    a = make()
    a.respond("take a note buy milk")
    assert "buy milk" in a.respond("read my notes")


def test_help_and_exit():
    a = make()
    assert "help" in a.respond("help").lower()
    assert a.is_exit("exit") and a.is_exit("bye")
    assert not a.is_exit("hello")


def test_skills_and_intents_loaded():
    a = make()
    assert len(a.skills) == 8
    assert len(a.intents) >= 20


def test_memory_persists_and_clears(tmp_path, monkeypatch):
    import pglu.memory as mem
    f = tmp_path / "memory.json"
    monkeypatch.setattr(mem, "MEM_FILE", str(f))
    a = Assistant(Config(), brain=_FakeBrain())
    a.respond("i love you")                       # chat -> brain -> remembered + saved
    assert f.exists()
    b = Assistant(Config(), brain=_FakeBrain())    # new session loads prior memory
    assert any("i love you" in m["content"] for m in b.history)
    b.respond("forget everything")                 # memory skill clears it
    assert mem.load() == []


def test_doctor_runs():
    assert "Pglu doctor" in make().doctor()


def test_persona_prompt():
    cfg = Config()
    cfg.name = "Friday"; cfg.user_name = "Tony"; cfg.persona = "loving"
    p = build_system_prompt(cfg)
    assert "Friday" in p and "Tony" in p


class _FakeBrain:
    def available(self):
        return True

    def effective_provider(self):
        return "fake"

    def reply(self, system, messages):
        return "FAKE:" + messages[-1]["content"]


def _cfg_nomem():
    c = Config()
    c.memory_enabled = False   # don't touch the real ~/.pglu/memory.json during tests
    return c


def test_brain_handles_chat_but_tools_stay_local():
    a = Assistant(_cfg_nomem(), brain=_FakeBrain())
    assert "100" in a.respond("what is 25 times 4")          # math = local tool, not the brain
    assert a.respond("i love you").startswith("FAKE:")        # open chat -> brain
    assert a.respond("hello").startswith("FAKE:")             # greeting defers to brain
    assert a.respond("tell me about yourself").startswith("FAKE:")   # self/knowledge -> brain
    assert a.respond("who is Alan Turing").startswith("FAKE:")       # knowledge -> brain


def test_run_command_returns_real_output():
    out = make().respond("cmd echo pglutest123")
    assert "pglutest123" in out


def test_offline_greeting_without_brain():
    r = make().respond("hello")  # no brain
    assert r and "FAKE" not in r
