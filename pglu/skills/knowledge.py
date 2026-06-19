"""Knowledge: time, date, math, Wikipedia answers, weather (key-less APIs)."""

from __future__ import annotations

import datetime as _dt

from .base import Skill
from ..util import get_json, quote, safe_math

_WCODE = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast", 45: "fog", 48: "freezing fog",
    51: "light drizzle", 53: "drizzle", 55: "dense drizzle", 61: "light rain", 63: "rain", 65: "heavy rain",
    71: "light snow", 73: "snow", 75: "heavy snow", 80: "rain showers", 81: "rain showers", 82: "violent showers",
    95: "thunderstorm", 96: "thunderstorm w/ hail", 99: "severe thunderstorm",
}


class Knowledge(Skill):
    name = "knowledge"
    priority = 60

    def intents(self):
        return [
            (r"\bwhat'?s? the time\b|\bwhat time is it\b|\btell me the time\b|\btime now\b", self.time),
            (r"\bwhat'?s?(?: the)?(?: today'?s)? date\b|\bwhat day is it\b|\btoday'?s date\b|\bcurrent date\b", self.date),
            (r"\b(?:calculate|compute|what is|what'?s|how much is)\b.*[\d].*[-+*/%]|\b\d+\s*(?:plus|minus|times|multiplied by|divided by|into|over|mod|power)\b", self.math),
            (r"\bweather(?:\s+(?:in|at|for)\s+(?P<city>[a-z .'-]+))?", self.weather),
            (r"\b(?:who(?:'s| is| was| are)|what(?:'s| is| was| are)|define|tell me about|explain)\s+(?P<q>.+)", self.wiki),
        ]

    def examples(self):
        return ["what time is it", "what's the date", "what is 24 times 7",
                "weather in Mumbai", "who is Ada Lovelace", "what is quantum computing"]

    def time(self, text, m):
        return "It's " + _dt.datetime.now().strftime("%I:%M %p").lstrip("0") + "."

    def date(self, text, m):
        return "Today is " + _dt.datetime.now().strftime("%A, %d %B %Y") + "."

    def math(self, text, m):
        val = safe_math(text)
        return f"That's {val}." if val is not None else None  # None → let other intents try

    def weather(self, text, m):
        city = (m.groupdict().get("city") or self.ctx.config.default_city or "").strip()
        if not city:
            return "Which city? Try “weather in Delhi”."
        try:
            geo = get_json(f"https://geocoding-api.open-meteo.com/v1/search?name={quote(city)}&count=1")
            if not geo.get("results"):
                return f"I couldn't find a place called {city}."
            g = geo["results"][0]
            f = get_json(f"https://api.open-meteo.com/v1/forecast?latitude={g['latitude']}&longitude={g['longitude']}&current_weather=true")
            w = f["current_weather"]
            return (f"It's {round(w['temperature'])}°C with {_WCODE.get(w['weathercode'], 'variable conditions')} "
                    f"in {g['name']}, {g.get('country', '')}. Wind around {round(w['windspeed'])} km/h.")
        except Exception:
            return "I couldn't reach the weather service. Check your connection."

    def wiki(self, text, m):
        q = m.group("q").strip().rstrip("?.")
        # math like "what is 2+2"
        if safe_math(q) is not None:
            return f"That's {safe_math(q)}."
        # self/opinion questions → the AI brain (not Wikipedia)
        if self.ctx.brain_available and q.lower() in (
                "yourself", "you", "urself", "your self", "me", "myself", "us"):
            return None
        # grounded factual lookup first (accurate for real people/things)
        try:
            d = get_json("https://en.wikipedia.org/api/rest_v1/page/summary/" + quote(q))
            if d.get("extract"):
                return d["extract"]
        except Exception:
            pass
        # not on Wikipedia → let the AI answer (it may know, or admit it doesn't)
        if self.ctx.brain_available:
            return None
        return f"I couldn't find that. Try “search {q}” to look it up on the web."
