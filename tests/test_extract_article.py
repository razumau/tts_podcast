import unittest
from extract_article import extract_webpage_content


class TestExtractArticle(unittest.TestCase):
    def test_extract_article(self):
        title, contents = extract_webpage_content("tests/economy.html")
        self.assertEqual(title, "The Divine Economy")
        self.assertEqual("Paul Seabright’s new book The Divine Economy", contents[:44])


if __name__ == "__main__":
    unittest.main()
