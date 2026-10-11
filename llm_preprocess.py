import os

import anthropic

SYSTEM_PROMPT = """You are a professional audio producer who adapts written articles for podcast narration.
Your job is to slightly adjust the given article text so it sounds better when read aloud by a text-to-speech system."""

REWRITE_PROMPT = """Update the following article for audio narration. Follow these rules strictly:

1. Remove all URLs, email addresses, and hyperlinks entirely.
2. Remove code blocks. If a code block is central to the article’s point, briefly describe what it does in one sentence.
3. Convert tables to short prose descriptions.
4. Remove all citation markers like [1], [2], etc.
5. Remove references to figures, images, charts, or any visual elements (e.g. "see Figure 3", "as shown below").
6. Expand abbreviations: "e.g." → "for example", "i.e." → "that is", "etc." → "et cetera".
7. Write out numbers as words when appropriate. This includes years.
8. Remove all markdown formatting (headers, bold, italic, links).
9. Keep the content faithful to the original — do not add or rewrite anything that isn’t covered by the rules above.
10. Output ONLY the rewritten text, nothing else.
11. Add correct pronunciation for uncommon non-English names using this format, similar to Markdown links: [Medici](/mˈɛdɪtʃi/). 
Article text:

{text}"""


async def rewrite_for_audio(text: str) -> str:
    """Use Claude to rewrite article text for audio narration."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required for LLM preprocessing")

    client = anthropic.AsyncAnthropic(api_key=api_key)

    async with client.beta.messages.stream(
        model="claude-sonnet-5-5",
        max_tokens=64000,
        # Mechanical rewrite: low effort keeps thinking short; Sonnet 5.5 defaults to high
        output_config={"effort": "low"},
        # Retry cyber-category refusals (e.g. security articles) on another model server-side
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": REWRITE_PROMPT.format(text=text)},
        ],
    ) as stream:
        result = await stream.get_final_message()

    if result.stop_reason == "refusal":
        print(f"Warning: LLM preprocessing was declined ({result.stop_details}), using input text as is")
        return text

    if result.stop_reason == "max_tokens":
        print("Warning: LLM preprocessing output was truncated due to max_tokens limit")

    # Responses may start with a thinking block, so collect text blocks only
    return "".join(block.text for block in result.content if block.type == "text")
