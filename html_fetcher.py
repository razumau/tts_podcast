import re

import requests

SCRIPT_PATTERN = r"<[ ]*script.*?\/[ ]*script[ ]*>"
STYLE_PATTERN = r"<[ ]*style.*?\/[ ]*style[ ]*>"
META_PATTERN = r"<[ ]*meta.*?>"
COMMENT_PATTERN = r"<[ ]*!--.*?--[ ]*>"
LINK_PATTERN = r"<[ ]*link.*?>"
BASE64_IMG_PATTERN = r'<img[^>]+src="data:image/[^;]+;base64,[^"]+"[^>]*>'
SVG_PATTERN = r"(<svg[^>]*>)(.*?)(<\/svg>)"


class HTMLCleaner:
    def __init__(self, html: str, clean_svg: bool = False, clean_base64: bool = False):
        self.html = html
        self.clean_svg = clean_svg
        self.clean_base64 = clean_base64

    def run(self):
        return self.clean_html()

    def replace_svg(self, new_content: str = ""):
        self.html = re.sub(
            SVG_PATTERN,
            lambda match: f"{match.group(1)}{new_content}{match.group(3)}",
            self.html,
            flags=re.DOTALL,
        )

    def replace_base64_images(self, new_image_src: str = "#"):
        self.html = re.sub(
            BASE64_IMG_PATTERN, f'<img src="{new_image_src}"/>', self.html
        )

    def remove_script(self):
        self.html = re.sub(
            SCRIPT_PATTERN,
            "",
            self.html,
            flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )

    def remove_style(self):
        self.html = re.sub(
            STYLE_PATTERN, "", self.html, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL
        )

    def remove_meta(self):
        self.html = re.sub(
            META_PATTERN, "", self.html, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL
        )

    def remove_comment(self):
        self.html = re.sub(
            COMMENT_PATTERN,
            "",
            self.html,
            flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )

    def remove_link(self):
        self.html = re.sub(
            LINK_PATTERN, "", self.html, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL
        )

    def clean_html(self):
        self.remove_script()
        self.remove_style()
        self.remove_meta()
        self.remove_comment()
        self.remove_link()

        if self.clean_svg:
            self.replace_svg()
        if self.clean_base64:
            self.replace_base64_images()
        return self.html


def get_clean_html_from_url(url: str) -> str:
    return HTMLCleaner(requests.get(url).text, clean_svg=True, clean_base64=True).run()
