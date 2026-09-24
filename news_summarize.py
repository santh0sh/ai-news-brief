"""Optional Gemini polish. Free AI Studio key, one call per run.
No key or any error: the brief still ships, just without the one-line notes."""

import json
import os

import requests

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

PROMPT = """You write a daily AI news brief for a senior software engineer.
Style rules: one line per item, plain words, say why it matters in at most 8 words. No hype, no emoji.

Here are today's candidate stories (numbered):
{stories}

Reply with ONLY these lines, no intro, no markdown:
1. <why it matters>
2. <why it matters>
... for each story number you were given."""


def summarize(stories, api_key=None, timeout=30):
    """Return {story_number: one-line note}. Empty dict on any failure."""
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key or not stories:
        return {}
    listing = "\n".join(f"{i}. {s.title} ({s.source})" for i, s in enumerate(stories, 1))
    body = {"contents": [{"parts": [{"text": PROMPT.format(stories=listing)}]}]}
    try:
        response = requests.post(f"{GEMINI_URL}?key={api_key}", json=body, timeout=timeout)
        response.raise_for_status()
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:  # noqa: BLE001 - polish is optional, the brief must always ship
        return {}
    notes = {}
    for line in text.strip().splitlines():
        head, _, note = line.partition(".")
        if head.strip().isdigit() and note.strip():
            notes[int(head.strip())] = note.strip()
    return notes
