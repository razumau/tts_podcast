import os

import anthropic

SYSTEM_PROMPT = """You are a podcast script writer. You transform articles into natural two-person dialogue scripts.
Speaker 1 [S1] is the host who introduces topics and asks questions.
Speaker 2 [S2] is the expert who explains and provides insight.
Output ONLY the dialogue script, nothing else."""

DIALOGUE_PROMPT = """Transform the following article into a natural two-person podcast dialogue script.

Rules:
1. Use [S1] and [S2] tags to mark speakers. Always start with [S1].
2. [S1] is the host — introduces topics, asks clarifying questions, reacts naturally.
3. [S2] is the knowledgeable guest — explains concepts, provides detail, gives examples.
4. Make the conversation natural and engaging, not a dry reading.
5. Cover all key points from the article faithfully — do not invent facts.
6. Remove all URLs, code blocks, citations, and visual references.
7. Keep the total length similar to the original article.
8. Each speaker turn should be 1-3 sentences. Avoid long monologues.
9. Add natural transitions: "That's a great point", "So what you're saying is...", etc.
10. Output ONLY the dialogue lines with speaker tags. No stage directions except for (laughs) sparingly.

Article:

{text}"""


def generate_dialogue_script(text: str) -> str:
    """Use Claude to convert article text into a two-speaker podcast dialogue."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required for dialogue generation")

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": DIALOGUE_PROMPT.format(text=text)},
        ],
    )

    return message.content[0].text
