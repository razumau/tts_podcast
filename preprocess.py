import re

from num2words import num2words

ABBREVIATIONS = {
    "e.g.": "for example",
    "i.e.": "that is",
    "etc.": "et cetera",
    "vs.": "versus",
    "approx.": "approximately",
    "dept.": "department",
    "govt.": "government",
    "avg.": "average",
    "est.": "established",
    "incl.": "including",
    "w/": "with",
    "w/o": "without",
}

TITLE_ABBREVIATIONS = {
    "Dr.": "Doctor",
    "Mr.": "Mister",
    "Mrs.": "Misses",
    "Ms.": "Ms",
    "Prof.": "Professor",
    "Sr.": "Senior",
    "Jr.": "Junior",
    "St.": "Saint",
    "Gen.": "General",
    "Gov.": "Governor",
    "Sgt.": "Sergeant",
    "Capt.": "Captain",
    "Lt.": "Lieutenant",
    "Col.": "Colonel",
    "Rev.": "Reverend",
}


def _remove_urls(text: str) -> str:
    return re.sub(r"https?://\S+", "", text)


def _remove_emails(text: str) -> str:
    return re.sub(r"[\w.\-+]+@[\w.\-]+\.\w+", "", text)


def _remove_citation_markers(text: str) -> str:
    return re.sub(r"\[\d+\]", "", text)


def _remove_markdown_images(text: str) -> str:
    return re.sub(r"!\[.*?\]\(.*?\)", "", text)


def _convert_markdown_links(text: str) -> str:
    """Keep the link text, remove the URL."""
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)


def _remove_code_blocks(text: str) -> str:
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"~~~[\s\S]*?~~~", "", text)
    return text


def _remove_inline_code(text: str) -> str:
    return re.sub(r"`([^`]+)`", r"\1", text)


def _remove_markdown_headers(text: str) -> str:
    return re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)


def _remove_markdown_formatting(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)
    text = re.sub(r"~~(.+?)~~", r"\1", text)
    return text


def _expand_abbreviations(text: str) -> str:
    for abbr, expanded in TITLE_ABBREVIATIONS.items():
        text = re.sub(re.escape(abbr) + r"(?=\s)", expanded, text)
    for abbr, expanded in ABBREVIATIONS.items():
        text = text.replace(abbr, expanded)
    return text


def _expand_numbers(text: str) -> str:
    """Convert standalone numbers to words. Handles integers, decimals, percentages, and currency."""

    def _replace_currency(match):
        symbol = match.group(1)
        amount = match.group(2)
        currency_names = {"$": "dollars", "€": "euros", "£": "pounds"}
        try:
            num = float(amount.replace(",", ""))
            words = num2words(num)
            return f"{words} {currency_names.get(symbol, symbol)}"
        except (ValueError, OverflowError):
            return match.group(0)

    text = re.sub(r"([$€£])([\d,]+\.?\d*)", _replace_currency, text)

    def _replace_percentage(match):
        try:
            num = float(match.group(1).replace(",", ""))
            return f"{num2words(num)} percent"
        except (ValueError, OverflowError):
            return match.group(0)

    text = re.sub(r"([\d,]+\.?\d*)%", _replace_percentage, text)

    def _replace_number(match):
        num_str = match.group(0).replace(",", "")
        try:
            if "." in num_str:
                num = float(num_str)
            else:
                num = int(num_str)
            if isinstance(num, int) and 1900 <= num <= 2100:
                return num2words(num, to="year")
            return num2words(num)
        except (ValueError, OverflowError):
            return match.group(0)

    text = re.sub(r"(?<!\w)[\d,]+\.?\d*(?!\w)", _replace_number, text)

    return text


def _remove_html_entities(text: str) -> str:
    text = text.replace("&amp;", "and")
    text = text.replace("&nbsp;", " ")
    text = text.replace("&lt;", "")
    text = text.replace("&gt;", "")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    text = re.sub(r"&\w+;", "", text)
    return text


def _normalize_whitespace(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()


def _remove_parenthetical_refs(text: str) -> str:
    """Remove visual references like (see Figure 3), (Table 2), (Fig. 1)."""
    text = re.sub(r"\(see\s+(?:Figure|Fig\.|Table|Chart|Graph|Diagram)\s*\d*\)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\((?:Figure|Fig\.|Table|Chart|Graph|Diagram)\s*\d+\)", "", text, flags=re.IGNORECASE)
    return text


def preprocess_for_tts(text: str) -> str:
    """Clean and normalize article text for text-to-speech consumption."""
    text = _remove_code_blocks(text)
    text = _remove_markdown_images(text)
    text = _convert_markdown_links(text)
    text = _remove_inline_code(text)
    text = _remove_markdown_headers(text)
    text = _remove_markdown_formatting(text)
    text = _remove_urls(text)
    text = _remove_emails(text)
    text = _remove_citation_markers(text)
    text = _remove_parenthetical_refs(text)
    text = _remove_html_entities(text)
    text = _expand_abbreviations(text)
    text = _expand_numbers(text)
    text = _normalize_whitespace(text)
    return text
