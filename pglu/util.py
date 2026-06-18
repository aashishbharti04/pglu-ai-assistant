"""Dependency-free helpers: HTTP JSON via urllib, and a safe math evaluator."""

from __future__ import annotations

import ast
import json
import operator
import urllib.parse
import urllib.request

USER_AGENT = "Pglu-AI-Assistant/1.0 (https://github.com/aashishbharti04/pglu-ai-assistant)"


def get_json(url: str, timeout: int = 8):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def quote(s: str) -> str:
    return urllib.parse.quote(s)


# ---- safe arithmetic (no eval) ----
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv, ast.USub: operator.neg, ast.UAdd: operator.pos,
}
_WORDS = [
    ("plus", "+"), ("added to", "+"), ("minus", "-"), ("subtract", "-"),
    ("multiplied by", "*"), ("times", "*"), ("into", "*"),
    ("divided by", "/"), ("over", "/"), ("power of", "**"), ("to the power", "**"),
    ("percent of", "/100*"), ("mod", "%"),
]


def safe_math(expr: str):
    """Evaluate a basic arithmetic expression. Returns a number or None."""
    e = " " + expr.lower() + " "
    for w, op in _WORDS:
        e = e.replace(" " + w + " ", op)
    e = "".join(c for c in e if c in "0123456789+-*/%.() ")
    e = e.strip()
    if not e or not any(c.isdigit() for c in e):
        return None
    try:
        node = ast.parse(e, mode="eval").body
        val = _ev(node)
        if isinstance(val, float) and val.is_integer():
            val = int(val)
        return round(val, 8) if isinstance(val, float) else val
    except Exception:
        return None


def _ev(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_ev(node.left), _ev(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_ev(node.operand))
    raise ValueError("unsupported expression")
