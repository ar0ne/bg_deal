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


def text_contains(text: str, query: str) -> bool:
    """True if text contains query string"""
    words = query.split(" ")
    # filter short words (e.g. 'and', 'or')
    words = list(filter(lambda x: len(x) > 3, words))
    for word in words:
        if re.search(word, text, re.IGNORECASE):
            return True
    return False
