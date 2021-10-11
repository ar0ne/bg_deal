"""
App endpoints
"""
import itertools
from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from bgd.containers import ApplicationContainer
from bgd.responses import GameSearchResult
from bgd.services import DataSource

router = APIRouter()


@router.get("/search/{game}", response_model=List[GameSearchResult])
@inject
async def search_game(
    game: str,
    data_sources: List[DataSource] = Depends(
        Provide[ApplicationContainer.data_sources]
    ),
) -> List[GameSearchResult]:
    """Search game endpoint"""
    results = [await source.search(game) for source in data_sources]
    return list(itertools.chain.from_iterable(results))
