"""
App endpoints
"""
import asyncio
from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_cache.decorator import cache
from sse_starlette import EventSourceResponse  # pylint: disable=E0401
from starlette.responses import JSONResponse

from bgd.containers import ApplicationContainer
from bgd.responses import GameDetailsResult
from bgd.services.base import GameInfoService, GameSearchService, SuggestGameService
from bgd.utils import game_deals_finder

INDEX_PAGE = "index.html"
API_VERSION = "/api/v1"

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
@inject
async def index_page(
    request: Request,
    templates: Jinja2Templates = Depends(Provide[ApplicationContainer.templates]),
):
    """Server sent events demo page"""
    return templates.TemplateResponse(INDEX_PAGE, {"request": request})


@router.get(API_VERSION + "/game-info/{game}", response_model=GameDetailsResult)
@inject
@cache()
async def game_info(
    game: str,
    board_game_geek: GameInfoService = Depends(Provide[ApplicationContainer.bgg_service]),
    tesera: GameInfoService = Depends(Provide[ApplicationContainer.tesera_service]),
):
    """Fetches board game info from provider"""
    board_game_info = await asyncio.gather(
        board_game_geek.get_board_game_info(game), return_exceptions=True
    )
    if isinstance(board_game_info[0], GameDetailsResult):
        return board_game_info[0]
    # if not found, will try to fall back to result from Tesera
    return await tesera.get_board_game_info(game)


@router.get(API_VERSION + "/stream-search/")
@inject
async def search_game_streamed(
    game: str,
    request: Request,
    data_sources: List[GameSearchService] = Depends(Provide[ApplicationContainer.data_sources]),
):
    """Find game deals"""
    game_deals = game_deals_finder(request, game, data_sources)
    return EventSourceResponse(game_deals)


@router.get(API_VERSION + "/game-suggests", response_class=JSONResponse)
@inject
async def suggest_game(
    _: Request,
    suggest_game_service: SuggestGameService = Depends(
        Provide[ApplicationContainer.suggest_game_service]
    ),
):
    """Suggest good game"""
    suggested_game = await suggest_game_service.suggest()
    return JSONResponse({"game": suggested_game})
