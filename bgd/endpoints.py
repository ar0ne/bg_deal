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
from sse_starlette import EventSourceResponse  # pylint: disable=E0401

from bgd.containers import ApplicationContainer
from bgd.responses import GameDetailsResult, GameSearchResult
from bgd.services.base import GameInfoService, GameSearchService, SuggestGameService
from bgd.utils import game_deals_finder, game_search_result_price

INDEX_PAGE = "index.html"
SEARCH_PAGE = "search.html"

router = APIRouter()


@router.get("/api/v1/search/{game}", response_model=List[GameSearchResult])
@inject
async def search_game(
    game: str,
    data_sources: List[GameSearchService] = Depends(Provide[ApplicationContainer.data_sources]),
) -> List[GameSearchResult]:
    """Search game endpoint"""
    results = [await source.search(game) for source in data_sources]
    combined_results = list(itertools.chain.from_iterable(results))
    combined_results.sort(key=game_search_result_price)
    return combined_results


@router.get("/api/v1/games/{game}", response_model=GameDetailsResult)
@inject
async def game_details(
    game: str,
    board_game_geek: GameInfoService = Depends(Provide[ApplicationContainer.bgg_service]),
    tesera: GameInfoService = Depends(Provide[ApplicationContainer.tesera_service]),
):
    """Fetches board game info from provider"""
    game_info = await asyncio.gather(
        board_game_geek.get_board_game_info(game), return_exceptions=True
    )
    if isinstance(game_info[0], GameDetailsResult):
        return game_info[0]
    # if not found, will try to fall back to result from Tesera
    return await tesera.get_board_game_info(game)


@router.get("/", response_class=HTMLResponse)
@inject
async def main_page(
    request: Request,
    templates: Jinja2Templates = Depends(Provide[ApplicationContainer.templates]),
    suggest_game_service: SuggestGameService = Depends(
        Provide[ApplicationContainer.suggest_game_service]
    ),
):
    """Render main page"""
    suggested_game = await suggest_game_service.suggest()
    return templates.TemplateResponse(
        INDEX_PAGE,
        {
            "request": request,
            "suggested_game": suggested_game,
        },
    )


@router.get("/search", response_class=HTMLResponse)
@inject
async def search_page(
    request: Request,
    name: str,
    templates: Jinja2Templates = Depends(Provide[ApplicationContainer.templates]),
):
    """Render Search page"""
    results = await search_game(name)
    game_info = await asyncio.gather(game_details(name), return_exceptions=True)
    game_info_extracted = game_info[0] if isinstance(game_info[0], GameDetailsResult) else None
    return templates.TemplateResponse(
        SEARCH_PAGE,
        {
            "request": request,
            "name": name,
            "results": results,
            "game_info": game_info_extracted,
        },
    )


@router.get("/sse", response_class=HTMLResponse)
@inject
async def sse_page(
    request: Request,
    suggest_game_service: SuggestGameService = Depends(
        Provide[ApplicationContainer.suggest_game_service]
    ),
    templates: Jinja2Templates = Depends(Provide[ApplicationContainer.templates]),
):
    """Server sent events demo page"""
    suggested_game = await suggest_game_service.suggest()
    return templates.TemplateResponse(
        "sse.html", {"request": request, "suggested_game": suggested_game}
    )


@router.get("/api/v1/stream/games")
@inject
async def find_game(
    game: str,
    request: Request,
    data_sources: List[GameSearchService] = Depends(Provide[ApplicationContainer.data_sources]),
):
    """Find game deals"""
    game_deals = game_deals_finder(request, game, data_sources)
    return EventSourceResponse(game_deals)
