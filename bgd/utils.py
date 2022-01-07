"""
App utilities.
"""
import json
import logging
from typing import List

from fastapi import Request

from bgd.services.base import GameSearchService

logger = logging.getLogger(__name__)


STREAM_RETRY_TIMEOUT = 30000  # milliseconds


async def game_deals_finder(
    request: Request,
    game: str,
    data_sources: List[GameSearchService],
):
    """Game finder generator"""
    while True:
        if await request.is_disconnected():
            logger.debug("Request disconnected.")
            break

        for source in data_sources:
            deals = await source.search(game)
            if deals:
                yield {
                    "event": "update",
                    "retry": STREAM_RETRY_TIMEOUT,
                    "data": json.dumps(deals),  # convert to json-string
                }

        logger.debug("We processed all data sources. Close connection.")
        yield {
            "event": "end",
            "data": "",
        }
