"""Skill registry — add a skill class here and it's auto-loaded."""

from .system import System
from .apps import Apps
from .web import Web
from .productivity import Productivity
from .fun import Fun
from .knowledge import Knowledge
from .memory import Memory

SKILL_CLASSES = [Memory, System, Apps, Web, Productivity, Fun, Knowledge]


def build_skills(ctx):
    return [cls(ctx) for cls in SKILL_CLASSES]
