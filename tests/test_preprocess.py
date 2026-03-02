import unittest

from preprocess import preprocess_for_tts


class TestPreprocess(unittest.TestCase):
    def test_removes_urls(self):
        text = "Check out https://example.com/path?q=1 for more info"
        result = preprocess_for_tts(text)
        self.assertNotIn("https://", result)
        self.assertIn("Check out", result)
        self.assertIn("for more info", result)

    def test_removes_emails(self):
        text = "Contact us at support@example.com for help"
        result = preprocess_for_tts(text)
        self.assertNotIn("support@example.com", result)

    def test_removes_citation_markers(self):
        text = "As shown in the study [1], results improved [23]"
        result = preprocess_for_tts(text)
        self.assertNotIn("[1]", result)
        self.assertNotIn("[23]", result)

    def test_converts_markdown_links(self):
        text = "See the [documentation](https://docs.example.com) for details"
        result = preprocess_for_tts(text)
        self.assertIn("documentation", result)
        self.assertNotIn("https://", result)
        self.assertNotIn("[", result)

    def test_removes_code_blocks(self):
        text = "Here is an example:\n```python\nprint('hello')\n```\nThat was it."
        result = preprocess_for_tts(text)
        self.assertNotIn("print", result)
        self.assertIn("Here is an example:", result)
        self.assertIn("That was it.", result)

    def test_removes_inline_code(self):
        text = "Use the `map` function"
        result = preprocess_for_tts(text)
        self.assertIn("map", result)
        self.assertNotIn("`", result)

    def test_expands_abbreviations(self):
        text = "There are many options, e.g. Python, Rust, etc."
        result = preprocess_for_tts(text)
        self.assertIn("for example", result)
        self.assertIn("et cetera", result)

    def test_expands_title_abbreviations(self):
        text = "Dr. Smith gave a talk"
        result = preprocess_for_tts(text)
        self.assertIn("Doctor", result)

    def test_expands_numbers(self):
        text = "There were 42 participants"
        result = preprocess_for_tts(text)
        self.assertIn("forty-two", result)

    def test_expands_currency(self):
        text = "The cost was $50"
        result = preprocess_for_tts(text)
        self.assertIn("fifty", result)
        self.assertIn("dollars", result)

    def test_expands_percentages(self):
        text = "Growth was 15%"
        result = preprocess_for_tts(text)
        self.assertIn("fifteen", result)
        self.assertIn("percent", result)

    def test_removes_markdown_formatting(self):
        text = "This is **bold** and *italic* text"
        result = preprocess_for_tts(text)
        self.assertIn("bold", result)
        self.assertIn("italic", result)
        self.assertNotIn("**", result)
        self.assertNotIn("*italic*", result)

    def test_removes_figure_references(self):
        text = "As shown (see Figure 3), the results improved"
        result = preprocess_for_tts(text)
        self.assertNotIn("Figure 3", result)

    def test_normalizes_whitespace(self):
        text = "Hello\n\n\n\n\nWorld"
        result = preprocess_for_tts(text)
        self.assertNotIn("\n\n\n", result)

    def test_full_pipeline(self):
        text = """# Introduction

        Check out https://example.com for more info [1].

        Dr. Smith found that 42 participants spent $50 each,
        resulting in a 15% increase.

        ```python
        print("hello world")
        ```

        As shown (see Figure 3), the **bold** claim is supported.

        Contact support@test.com for questions, e.g. pricing etc."""

        result = preprocess_for_tts(text)
        self.assertNotIn("https://", result)
        self.assertNotIn("[1]", result)
        self.assertNotIn("```", result)
        self.assertNotIn("support@test.com", result)
        self.assertNotIn("**", result)
        self.assertIn("Doctor", result)
        self.assertIn("forty-two", result)
        self.assertIn("for example", result)


if __name__ == "__main__":
    unittest.main()
