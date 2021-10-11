"""
App utils
"""
import math


def convert_byn_to_usd(byn_in_cents: int) -> int:
    """Convert prices from BYN to USD"""
    exchange_rate = 250  # @todo: do not hardcode it
    return math.floor(byn_in_cents * 100 / exchange_rate)
