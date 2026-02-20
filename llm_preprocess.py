import os

import anthropic

SYSTEM_PROMPT = """You are a professional audio producer who adapts written articles for podcast narration.
Your job is to rewrite the given article text so it sounds natural when read aloud by a text-to-speech system."""

REWRITE_PROMPT = """Rewrite the following article for audio narration. Follow these rules strictly:

1. Remove all URLs, email addresses, and hyperlinks entirely.
2. Remove code blocks. If a code block is central to the article's point, briefly describe what it does in one sentence.
3. Convert tables to natural prose descriptions.
4. Remove all citation markers like [1], [2], etc.
5. Remove references to figures, images, charts, or any visual elements (e.g. "see Figure 3", "as shown below").
6. Expand abbreviations: "e.g." → "for example", "i.e." → "that is", "etc." → "et cetera".
7. Write out numbers as words when appropriate (but keep years as numbers).
8. Remove all markdown formatting (headers, bold, italic, links).
9. Keep the content faithful to the original — do not add opinions, commentary, or new information.
10. Use natural spoken language with good sentence flow and clear transitions between sections.
11. Do not add an introduction or conclusion that wasn't in the original.
12. Output ONLY the rewritten text, nothing else.

Article text:

{text}"""


def rewrite_for_audio(text: str) -> str:
    """Use Claude to rewrite article text for audio narration."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required for LLM preprocessing")

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": REWRITE_PROMPT.format(text=text)},
        ],
    )

    return message.content[0].text
