"""
App endpoints
"""
import itertools
from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from bgd.containers import ApplicationContainer
from bgd.responses import SearchResponseItem
from bgd.services import SearchService

router = APIRouter()


@router.get("/search/{game}", response_model=List[SearchResponseItem])
@inject
async def search_game(
    game: str,
    search_engines: List[SearchService] = Depends(
        Provide[ApplicationContainer.search_engines]
    ),
) -> List[SearchResponseItem]:
    """Index endpoint"""
    results = [await searcher.search_games(game) for searcher in search_engines]
    return list(itertools.chain.from_iterable(results))
