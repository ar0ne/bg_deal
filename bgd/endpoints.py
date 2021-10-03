"""
App endpoints
"""
from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from bgd.containers import ApplicationContainer
from bgd.responses import SearchResponseItem
from bgd.services import KufarSearchService, WildberriesSearchService

router = APIRouter()


@router.get("/search/{game}", response_model=List[SearchResponseItem])
@inject
async def search_game(
    game: str,
    kufar_search_service: KufarSearchService = Depends(
        Provide[ApplicationContainer.kufar_search_service]
    ),
    wildberries_search_service: WildberriesSearchService = Depends(
        Provide[ApplicationContainer.wildberreis_search_service]
    ),
) -> List[SearchResponseItem]:
    """Index endpoint"""
    return [
        *kufar_search_service.search_games(game),
        *wildberries_search_service.search_games(game),
    ]
