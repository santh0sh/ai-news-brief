# ai-news-brief

A small agent that reads the day's AI news and writes a top 10 brief in my style: one line per item, no fluff. Free sources, free tools, zero cost to run.

Sample output (real run, 24 Sep 2026, no API keys):

```
# Top 10 AI news - Thursday, 24 September 2026

1. **Anthropic launches Claude Opus 5.5 with stricter safeguards for cybersecurity** (Hacker News)
2. **Japanese used bookstores see 5x sales surge as books are being bought by the ton** (Hacker News)
3. **Google tests letting Gemini call businesses for you** (TechCrunch AI)
4. **Artificial Symbiotic Intelligence** (Hacker News)
5. **Ando wants to take on Slack with a team messaging app that lets humans and agents work together** (TechCrunch AI)
...
```

## How it works

```
RSS feeds + Hacker News  ->  fetch  ->  dedupe + score  ->  top 10  ->  markdown brief
     (free, no keys)        sources.py      rank.py                     brief.py
                                                                       |
        optional: one-line "why it matters" notes (free Gemini key) ---+
        optional: send to WhatsApp (free Meta Cloud API) --------------+
```

- `news_sources.py` - TechCrunch AI, The Verge AI, VentureBeat AI, MIT Technology Review, Google News (AI query), Hacker News (Algolia API, last 48h). One dead source never sinks the run.
- `news_rank.py` - dedupes the same story across outlets, scores by source weight, signal keywords, freshness and HN points. Plain heuristics you can read and tune.
- `news_summarize.py` - optional Gemini pass for one-line notes. Any failure: the brief still ships without them.
- `news_deliver.py` - optional WhatsApp delivery via Meta's free Cloud API.
- `test_agent.py` - unittest suite, zero extra installs: `python -m unittest test_agent`

All files sit flat at the repo root - easy to upload from any device, including a phone.

## Run it (10 minutes)

```bash
git clone https://github.com/santh0sh/ai-news-brief.git
cd ai-news-brief
pip install -r requirements.txt
python main.py
```

Or just download the repo (Code > Download ZIP) if git is not your thing.

The brief lands in `output/` and prints to the console. No keys needed.

## Optional: Gemini notes (free)

1. Get a free key at https://aistudio.google.com/apikey
2. `cp .env.example .env` and paste it as `GEMINI_API_KEY`
3. `python main.py --llm`

## Optional: WhatsApp delivery (free)

Uses Meta's WhatsApp Cloud API test number - free, messages your own number.

1. Create a developer app at https://developers.facebook.com (type: Business)
2. Add the WhatsApp product, open API Setup
3. Copy the temporary access token and the test phone number ID
4. Add your own number as a recipient and verify the OTP Meta sends
5. Put `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_TO` (your number with country code, e.g. 91XXXXXXXXXX) in `.env`
6. `python main.py --llm --send-whatsapp`

The test token expires in 24h; the README section on going live covers the permanent token when needed.

## Run it daily

Windows (Task Scheduler): action `python`, arguments `C:\path\to\ai-news-brief\main.py --llm --send-whatsapp`, trigger daily 7:00 AM.

Linux/Mac (cron): `0 7 * * * cd /path/to/ai-news-brief && /usr/bin/python3 main.py --llm --send-whatsapp`

## Roadmap

- Resolve Google News redirect links to the real article URLs
- More sources (arXiv, company blogs)
- Web dashboard via GitHub Pages

Part of a public build series on applied AI agents. Next: a Spring Boot agent service built to enterprise standards (evals, guardrails, logging).

## Upload steps from a phone (5 minutes)

1. Create a public repo named exactly `ai-news-brief` on github.com (do not tick "Add a README")
2. Unzip this package anywhere (Files app works)
3. On the repo page: Add file > Upload files > select ALL the files > Commit
4. Flat layout on purpose: every file at root, no folders, so mobile upload just works
