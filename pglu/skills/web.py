"""Web: open sites and run searches in the default browser."""

from __future__ import annotations

import webbrowser

from .base import Skill
from ..util import quote

SITES = {
    "youtube": "https://youtube.com", "google": "https://google.com", "github": "https://github.com",
    "gmail": "https://mail.google.com", "maps": "https://maps.google.com", "twitter": "https://twitter.com",
    "x": "https://x.com", "linkedin": "https://linkedin.com", "instagram": "https://instagram.com",
    "whatsapp": "https://web.whatsapp.com", "netflix": "https://netflix.com", "reddit": "https://reddit.com",
    "amazon": "https://amazon.in", "flipkart": "https://flipkart.com", "spotify": "https://open.spotify.com",
    "stackoverflow": "https://stackoverflow.com", "chatgpt": "https://chat.openai.com",
}


class Web(Skill):
    name = "web"
    priority = 30

    def intents(self):
        # anchored to the START so mid-sentence words ("...does he play for?") aren't hijacked
        return [
            (r"^\s*(?:youtube|play)\s+(?P<q>.+)", self.youtube),
            (r"^\s*(?:search(?:\s+for)?|google|look\s+up)\s+(?P<q>.+)", self.search),
            (r"^\s*open\s+(?P<site>[\w.\- ]+)\s*$", self.open_site),
        ]

    def examples(self):
        return ["open youtube", "open github.com", "search for best laptops 2026", "youtube lofi beats"]

    def youtube(self, text, m):
        q = m.group("q").strip()
        webbrowser.open("https://www.youtube.com/results?search_query=" + quote(q))
        return f"Searching YouTube for {q}."

    def search(self, text, m):
        q = m.group("q").strip()
        webbrowser.open("https://www.google.com/search?q=" + quote(q))
        return f"Searching the web for {q}."

    def open_site(self, text, m):
        raw = m.group("site").strip().lower()
        key = raw.replace(" ", "")
        if key in SITES:
            url = SITES[key]
        elif "." in raw:
            url = raw if raw.startswith("http") else "https://" + raw
        else:
            # Apps already tried to launch it as a program; if we're here it's neither a
            # known app nor a website — answer honestly instead of letting the AI fake it.
            return (f"I couldn't find an app or website called “{raw}”. "
                    f"Try the exact name, or say “search {raw}”.")
        webbrowser.open(url)
        return f"Opening {raw}."
