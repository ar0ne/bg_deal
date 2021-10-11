"""
App endpoints
"""
import itertools
from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from bgd.containers import ApplicationContainer
from bgd.responses import GameDetailsResult, GameSearchResult
from bgd.services import BoardGameGeekService, DataSource

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


@router.get("/games/{game}", response_model=GameDetailsResult)
@inject
async def game_details(
    game: str,
    service: BoardGameGeekService = Depends(Provide[ApplicationContainer.bgg_service]),
):
    return await service.get_board_game_info(game)


@router.get("/", response_class=HTMLResponse)
@inject
async def main(
    request: Request,
    templates: Jinja2Templates = Depends(Provide[ApplicationContainer.templates]),
):
    return templates.TemplateResponse("index.html", {"request": request})
