"""
App endpoints
"""
from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from bgd.containers import ApplicationContainer
from bgd.responses import SearchResponseItem
from bgd.services import KufarSearchService

router = APIRouter()


@router.get("/search/{game}", response_model=List[SearchResponseItem])
@inject
async def search_game(
    game: str,
    search_service: KufarSearchService = Depends(
        Provide[ApplicationContainer.kufar_search_service]
    ),
    game_category: int = Depends(
        Provide[ApplicationContainer.config.kufar.game_category.as_int()]
    ),
) -> List[SearchResponseItem]:
    """Index endpoint"""
    return search_service.search_game_ads(game, game_category)
