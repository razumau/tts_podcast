import subprocess
import os

BUN_SCRIPT = 'extract_article.ts'
ARTICLE_TITLE_FILE = 'extracted_article_title.txt'
ARTICLE_FILE = 'extracted_article.txt'


def extract_webpage_content(url: str) -> tuple[str, str] or None:
    try:
        subprocess.run(['bun', BUN_SCRIPT, url], check=True)

        if not (os.path.exists(ARTICLE_FILE) and os.path.exists(ARTICLE_TITLE_FILE)):
            print(f"We expect input files at {ARTICLE_FILE} and {ARTICLE_TITLE_FILE}")
            return None

        with open(ARTICLE_TITLE_FILE, "r", encoding="utf-8") as f:
            title = f.read()
        os.remove(ARTICLE_TITLE_FILE)

        with open(ARTICLE_FILE, "r", encoding="utf-8") as f:
            contents = f.read()
        os.remove(ARTICLE_FILE)

        return title, contents
    except subprocess.CalledProcessError as e:
        print(f"Error running script: {e}")
        return None
