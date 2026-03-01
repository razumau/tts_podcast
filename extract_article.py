import subprocess
import os
import tempfile

BUN_SCRIPT = "extract_article.ts"


def extract_webpage_content(url: str) -> tuple[str, str] | None:
    # Use unique temp files to avoid concurrency issues
    with (
        tempfile.NamedTemporaryFile(mode="w", suffix="_article.txt", delete=False) as article_f,
        tempfile.NamedTemporaryFile(mode="w", suffix="_title.txt", delete=False) as title_f,
    ):
        article_path = article_f.name
        title_path = title_f.name

    try:
        subprocess.run(
            ["bun", BUN_SCRIPT, url, article_path, title_path],
            check=True,
        )

        if not (os.path.exists(article_path) and os.path.exists(title_path)):
            print(f"Expected output files at {article_path} and {title_path}")
            return None

        with open(title_path, "r", encoding="utf-8") as f:
            title = f.read()

        with open(article_path, "r", encoding="utf-8") as f:
            contents = f.read()

        return title, contents
    except subprocess.CalledProcessError as e:
        print(f"Error running script: {e}")
        return None
    finally:
        for path in (article_path, title_path):
            if os.path.exists(path):
                os.remove(path)
