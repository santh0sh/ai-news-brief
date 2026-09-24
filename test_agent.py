import unittest
from datetime import datetime, timedelta, timezone

import news_brief as brief
import news_rank as rank
from news_sources import Story


def story(title, source="TechCrunch AI", weight=1.2, hours_old=2, hn_points=0):
    return Story(title=title, url=f"https://example.com/{abs(hash(title))}",
                 source=source, weight=weight, hn_points=hn_points,
                 published=datetime.now(tz=timezone.utc) - timedelta(hours=hours_old))


class RankTests(unittest.TestCase):
    def test_dedupe_keeps_heavier_source(self):
        a = story("OpenAI launches new model", source="Google News", weight=0.9)
        b = story("OpenAI launches new model!", source="MIT Technology Review", weight=1.3)
        kept = rank.dedupe([a, b])
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0].source, "MIT Technology Review")

    def test_noise_is_dropped(self):
        noisy = story("Sponsored: best AI gadget deals")
        real = story("Anthropic releases new Claude model")
        top = rank.top_stories([noisy, real], n=5)
        self.assertEqual(top, [real])

    def test_fresh_beats_stale(self):
        fresh = story("Google announces Gemini update", hours_old=1)
        stale = story("Google announces Gemini update roadmap", hours_old=30)
        self.assertGreater(rank.score(fresh), rank.score(stale))

    def test_hn_heat_capped(self):
        hot = story("New open-source model", hn_points=5000)
        self.assertLessEqual(rank.score(hot) - rank.score(story("New open-source model")), 6)


class BriefTests(unittest.TestCase):
    def test_render_has_one_line_per_item(self):
        top = [story(f"Story {i}") for i in range(3)]
        text = brief.render(top)
        self.assertIn("# Top 10 AI news", text)
        self.assertIn("1. **Story 0**", text)
        self.assertIn("Sources read:", text)


if __name__ == "__main__":
    unittest.main()
