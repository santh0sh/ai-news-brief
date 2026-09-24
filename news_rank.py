"""Dedupe and score. Transparent heuristics - the same story from five sites
counts once, and what the community is excited about ranks higher."""

import re
from datetime import datetime, timezone

# Signals that a story is news, not noise. Add your own as you watch the output.
SIGNAL_WORDS = {
    "launch": 3, "launches": 3, "launched": 3, "release": 3, "releases": 3,
    "unveils": 3, "announces": 3, "announcement": 2, "funding": 3, "raises": 3,
    "billion": 2, "model": 2, "models": 2, "agent": 2, "agents": 2,
    "open-source": 2, "open source": 2, "benchmark": 2, "reasoning": 2,
    "gpt": 3, "claude": 3, "gemini": 3, "llama": 3, "openai": 3,
    "anthropic": 3, "deepmind": 2, "mistral": 2, "nvidia": 2,
    "google": 1, "meta": 1, "microsoft": 1, "apple": 1, "amazon": 1,
}

NOISE_WORDS = {"giveaway", "sponsored", "deal:", "discount", "coupon", "podcast"}


STOPWORDS = {"a", "an", "and", "the", "to", "of", "in", "on", "for", "with",
             "is", "it", "its", "as", "at", "by", "how", "why", "what", "you",
             "your", "that", "this", "now", "new", "s", "t"}


def _words(title: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", title.lower()) if w not in STOPWORDS}


def _overlap(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def dedupe(stories):
    """Drop near-duplicate stories (same news, different headline), keeping the
    one from the heavier source."""
    kept = []
    for story in sorted(stories, key=lambda s: -s.weight):
        words = _words(story.title)
        for other in kept:
            other_words = _words(other.title)
            same_story = (_overlap(words, other_words) >= 0.6
                          or len(words & other_words) >= 3)  # same entities, different headline
            if same_story:
                break
        else:
            kept.append(story)
    return kept


def score(story, now=None) -> float:
    now = now or datetime.now(tz=timezone.utc)
    text = story.title.lower()
    if any(word in text for word in NOISE_WORDS):
        return -1.0
    points = sum(weight for word, weight in SIGNAL_WORDS.items() if word in text)
    points += story.weight * 5
    age_hours = max((now - story.published).total_seconds() / 3600, 0)
    points += max(0, 12 - age_hours)  # fresher stories rank higher, decays over 12h
    points += min(story.hn_points / 50, 6)  # community heat, capped
    return round(points, 2)


def top_stories(stories, n=10):
    unique = dedupe(stories)
    scored = [(score(s), s) for s in unique]
    scored = [(sc, s) for sc, s in scored if sc >= 0]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [s for _, s in scored[:n]]
