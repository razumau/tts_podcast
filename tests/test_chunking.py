import unittest

from chunking import split_text


class TestSplitText(unittest.TestCase):
    def test_short_text_is_one_part(self):
        self.assertEqual(split_text("  Short text.\n", 100), ["Short text."])

    def test_splits_between_paragraphs(self):
        paragraphs = [f"Paragraph {i} " + "word " * 15 for i in range(10)]
        text = "\n\n".join(p.strip() for p in paragraphs)
        parts = split_text(text, 300)
        self.assertGreater(len(parts), 1)
        self.assertTrue(all(len(part) <= 300 for part in parts))
        self.assertEqual("\n\n".join(parts), text)

    def test_parts_are_balanced(self):
        # 21 paragraphs of 100 characters with a 1,000 limit: three parts of ~700, not 1,000 + 1,000 + 100
        text = "\n\n".join("x" * 98 + "." for _ in range(21))
        parts = split_text(text, 1000)
        self.assertEqual(len(parts), 3)
        self.assertEqual([len(part) for part in parts], [705, 705, 705])

    def test_balances_when_sentence_boundaries_need_an_extra_part(self):
        # 2,099 characters would fit in two parts of 1,050, but not at sentence boundaries:
        # three even parts rather than 1,049 + 1,049 + a 99-character sliver
        text = " ".join("x" * 98 + "." for _ in range(21))
        parts = split_text(text, 1050)
        self.assertEqual([len(part) for part in parts], [699, 699, 699])

    def test_text_without_newlines_splits_between_sentences(self):
        text = " ".join(f"This is sentence number {i}." for i in range(200))
        parts = split_text(text, 1000)
        self.assertTrue(all(len(part) <= 1000 for part in parts))
        self.assertTrue(all(part.endswith(".") for part in parts))
        self.assertEqual(" ".join(parts), text)

    def test_overlong_sentence_splits_between_words(self):
        text = "word " * 500
        parts = split_text(text, 300)
        self.assertTrue(all(len(part) <= 300 for part in parts))
        self.assertEqual(" ".join(parts), text.strip())

    def test_overlong_word_is_cut(self):
        parts = split_text("x" * 2500, 1000)
        self.assertTrue(all(len(part) <= 1000 for part in parts))
        self.assertEqual("".join(parts), "x" * 2500)


if __name__ == "__main__":
    unittest.main()
