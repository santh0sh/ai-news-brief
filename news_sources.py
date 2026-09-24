"""Where the news comes from. Free sources only: public RSS feeds and the
Hacker News Algolia API. No keys, no cost."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
import time

import feedparser
import requests

USER_AGENT = "ai-news-brief/1.0 (+https://github.com/santh0sh/ai-news-brief)"
TIMEOUT = 20

# Weight reflects how reliably the source breaks real AI news (not listicles).
FEEDS = [
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "weight": 1.2},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "weight": 1.1},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "weight": 1.1},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed", "weight": 1.3},
    {"name": "Google News", "url": "https://news.google.com/rss/search?q=artificial+intelligence+when:1d&hl=en-US&gl=US&ceid=US:en", "weight": 0.9, "needs_ai_keyword": True},
]

def hn_url(hours=48):
    since = int(time.time()) - hours * 3600
    return ("https://hn.algolia.com/api/v1/search_by_date?query=artificial%20intelligence"
            f"&tags=story&hitsPerPage=30&numericFilters=created_at_i>{since}")


@dataclass
class Story:
    title: str
    url: str
    source: str
    published: datetime
    weight: float = 1.0
    hn_points: int = 0
    errors: list = field(default_factory=list)


def _parse_time(entry) -> datetime:
    parsed = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if parsed:
        return datetime.fromtimestamp(time.mktime(parsed), tz=timezone.utc)
    return datetime.now(tz=timezone.utc)


def fetch_feeds(feeds=None):
    """Fetch every RSS feed. A dead feed costs a warning, never the run."""
    stories, errors = [], []
    for feed in (feeds or FEEDS):
        try:
            response = requests.get(feed["url"], headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
            response.raise_for_status()
            parsed = feedparser.parse(response.content)
            for entry in parsed.entries[:25]:
                title = (entry.get("title") or "").strip()
                link = (entry.get("link") or "").strip()
                if not title or not link:
                    continue
                if feed.get("needs_ai_keyword") and not re.search(
                        r"\b(ai|artificial intelligence|llm|gpt|claude|gemini|openai|anthropic|deepmind|machine learning|neural|agent|copilot|model)\b",
                        title.lower()):
                    continue  # Google News slips in off-topic hits
                stories.append(Story(title=title, url=link, source=feed["name"],
                                     published=_parse_time(entry), weight=feed["weight"]))
        except Exception as exc:  # noqa: BLE001 - one bad feed must not sink the brief
            errors.append(f"{feed['name']}: {exc}")
    return stories, errors


def fetch_hackernews():
    """Hacker News stories mentioning AI, via the free Algolia API."""
    try:
        response = requests.get(hn_url(), headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        response.raise_for_status()
        stories = []
        for hit in response.json().get("hits", []):
            title = (hit.get("title") or "").strip()
            url = (hit.get("url") or "").strip()
            if title and url:
                created = hit.get("created_at_i")
                published = (datetime.fromtimestamp(created, tz=timezone.utc)
                             if created else datetime.now(tz=timezone.utc))
                stories.append(Story(title=title, url=url, source="Hacker News",
                                     published=published, weight=1.0,
                                     hn_points=int(hit.get("points") or 0)))
        return stories, []
    except Exception as exc:  # noqa: BLE001
        return [], [f"Hacker News: {exc}"]


def fetch_all():
    stories, errors = fetch_feeds()
    hn, hn_errors = fetch_hackernews()
    return stories + hn, errors + hn_errors
