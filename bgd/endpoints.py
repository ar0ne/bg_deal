"""
App endpoints
"""
import asyncio
import itertools
from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from bgd.containers import ApplicationContainer
from bgd.responses import GameDetailsResult, GameSearchResult, Price
from bgd.services import BoardGameGeekService, DataSource

router = APIRouter()


def sort_by_price(game: GameSearchResult) -> int:
    """Sort function for game search results"""
    if not (game and game.price):
        return 0
    return game.price.byn


@router.get("/api/v1/search/{game}", response_model=List[GameSearchResult])
@inject
async def search_game(
    game: str,
    data_sources: List[DataSource] = Depends(
        Provide[ApplicationContainer.data_sources]
    ),
) -> List[GameSearchResult]:
    """Search game endpoint"""
    results = [await source.search(game) for source in data_sources]
    results = list(itertools.chain.from_iterable(results))
    results.sort(key=sort_by_price)
    return results


@router.get("/api/v1/games/{game}", response_model=GameDetailsResult)
@inject
async def game_details(
    game: str,
    service: BoardGameGeekService = Depends(Provide[ApplicationContainer.bgg_service]),
):
    return await service.get_board_game_info(game)


@router.get("/", response_class=HTMLResponse)
@inject
async def main_page(
    request: Request,
    templates: Jinja2Templates = Depends(Provide[ApplicationContainer.templates]),
):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/search", response_class=HTMLResponse)
@inject
async def search_page(
    request: Request,
    name: str,
    templates: Jinja2Templates = Depends(Provide[ApplicationContainer.templates]),
):
    results = await search_game(name)
    game_info = await asyncio.gather(game_details(name), return_exceptions=True)
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "name": name,
            "results": results,
            "game_info": game_info[0]
            if isinstance(game_info[0], GameDetailsResult)
            else None,
        },
    )
