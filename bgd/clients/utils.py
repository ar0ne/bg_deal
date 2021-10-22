"""
App utils
"""
import math
import re

HTML_TAGS_REGEXP = re.compile("<.*?>")


def convert_byn_to_usd(byn_in_cents: int) -> int:
    """Convert prices from BYN to USD"""
    exchange_rate = 250  # @todo: do not hardcode it
    return math.floor(byn_in_cents * 100 / exchange_rate)


def remove_backslashes(text: str) -> str:
    """Remove backslashes from input string"""
    return text.replace("\\", "")


def clean_html(raw_html: str) -> str:
    """Remove html tags from raw string"""
    return re.sub(HTML_TAGS_REGEXP, "", raw_html)
