"""Top 10 AI news, one run:

    python main.py                 # fetch, rank, write the brief to output/
    python main.py --llm           # add one-line "why it matters" notes (free Gemini key)
    python main.py --send-whatsapp # also send it to your WhatsApp (free Cloud API)
"""

import argparse
import os
from datetime import datetime
from pathlib import Path

import news_brief as brief
import news_deliver as deliver
import news_rank as rank
import news_sources as sources
import news_summarize as summarize


def main():
    parser = argparse.ArgumentParser(description="Daily top 10 AI news brief")
    parser.add_argument("--llm", action="store_true", help="use Gemini (free key) for one-line notes")
    parser.add_argument("--send-whatsapp", action="store_true", help="send the brief to WhatsApp")
    parser.add_argument("--out", default="output", help="folder for generated briefs")
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()

    stories, errors = sources.fetch_all()
    print(f"fetched {len(stories)} stories ({len(errors)} source errors)")
    if not stories:
        raise SystemExit(f"no stories fetched: {errors}")

    top = rank.top_stories(stories, n=args.top)
    notes = summarize.summarize(top) if args.llm else {}
    if args.llm and not notes:
        print("gemini notes unavailable - shipping the brief without them")

    text = brief.render(top, errors=errors, llm_notes=notes)
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"brief-{datetime.now():%Y-%m-%d}.md"
    path.write_text(text, encoding="utf-8")
    print(text)
    print(f"\nsaved: {path}")

    if args.send_whatsapp:
        ok, detail = deliver.send_whatsapp(text)
        print(f"whatsapp: {detail}")
        if not ok:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
