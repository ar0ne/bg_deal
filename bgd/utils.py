"""
App utilities.
"""
import logging
from typing import Any, List

import orjson
from fastapi import Request

from bgd.services.base import GameSearchService

logger = logging.getLogger(__name__)


STREAM_RETRY_TIMEOUT = 30000  # milliseconds


def serialize_event_data(data: Any) -> str:
    """Convert event data to JSON-string"""
    return orjson.dumps(data).decode("utf-8")


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
                    "data": serialize_event_data(deals),  # convert to json-string for frontend
                }

        logger.debug("We processed all data sources. Close connection.")
        yield {
            "event": "end",
            "data": "",
        }
