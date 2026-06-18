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
        return [
            (r"\b(?:youtube|play)\s+(?P<q>.+)", self.youtube),
            (r"\b(?:search(?:\s+for)?|google|look up|find)\s+(?P<q>.+)", self.search),
            (r"\bopen\s+(?P<site>[\w.\- ]+)", self.open_site),
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
            return None  # not a known site → let Apps/other skills try
        webbrowser.open(url)
        return f"Opening {raw}."
