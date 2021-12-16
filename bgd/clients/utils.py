"""
App utils
"""
import re

HTML_TAGS_REGEXP = re.compile("<.*?>")


def remove_backslashes(text: str) -> str:
    """Remove backslashes from input string"""
    return text.replace("\\", "")


def clean_html(raw_html: str) -> str:
    """Remove html tags from raw string"""
    return re.sub(HTML_TAGS_REGEXP, "", raw_html)
