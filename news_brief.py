"""Render the brief. His style: one line per item, no fluff."""

from datetime import datetime


def render(stories, when=None, errors=None, llm_notes=None) -> str:
    when = when or datetime.now()
    lines = [f"# Top 10 AI news - {when.strftime('%A, %-d %B %Y')}", ""]
    notes = llm_notes or {}
    for i, story in enumerate(stories, 1):
        note = notes.get(i)
        if note:
            lines.append(f"{i}. **{story.title}** - {note} ({story.source})")
        else:
            lines.append(f"{i}. **{story.title}** ({story.source})")
        lines.append(f"   {story.url}")
        lines.append("")
    sources = sorted({s.source for s in stories})
    lines.append(f"Sources read: {', '.join(sources)}.")
    if errors:
        lines.append(f"Skipped (source errors): {'; '.join(errors)}.")
    lines.append("Built by ai-news-brief.")
    return "\n".join(lines)
