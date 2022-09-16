"""
App endpoints
"""
import asyncio
from typing import Dict

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_cache.decorator import cache
from sse_starlette import EventSourceResponse  # pylint: disable=E0401
from starlette.responses import Response

from bgd.containers import ApplicationContainer
from bgd.responses import GameDetailsResult
from bgd.routes import (
    GAME_INFO_ROUTE,
    INDEX_HTML,
    INDEX_ROUTE,
    SEARCH_GAME_STREAM_ROUTE,
    SUGGEST_GAME_ROUTE,
)
from bgd.services.abc import SuggestGameService
from bgd.services.base import GameDealsSearchFacade, GameInfoService

router = APIRouter()


@router.get(INDEX_ROUTE, response_class=HTMLResponse)
@inject
async def index_page(
    request: Request,
    templates: Jinja2Templates = Depends(Provide[ApplicationContainer.templates]),
) -> Response:
    """Render index page"""
    return templates.TemplateResponse(INDEX_HTML, {"request": request})


@router.get(GAME_INFO_ROUTE, response_model=GameDetailsResult)
@inject
@cache()
async def game_info(
    game: str,
    board_game_geek: GameInfoService = Depends(Provide[ApplicationContainer.bgg_service]),
    tesera: GameInfoService = Depends(Provide[ApplicationContainer.tesera_service]),
) -> GameDetailsResult:
    """Fetches board game info from data providers (bgg and tesera)"""
    board_game_info = await asyncio.gather(
        board_game_geek.get_board_game_info(game), return_exceptions=True
    )
    if isinstance(board_game_info[0], GameDetailsResult):
        return board_game_info[0]
    # if not found, will try to fall back to result from Tesera
    return await tesera.get_board_game_info(game)


@router.get(SEARCH_GAME_STREAM_ROUTE)
@inject
async def search_game_streamed(
    game: str,
    request: Request,
    game_search_facade: GameDealsSearchFacade = Depends(
        Provide[ApplicationContainer.game_search_facade]
    ),
) -> Response:
    """Finds game deals"""
    game_deals = game_search_facade.find_game_deals(request, game)
    return EventSourceResponse(game_deals)


@router.get(SUGGEST_GAME_ROUTE)
@inject
async def suggest_game(
    _: Request,
    suggest_game_service: SuggestGameService = Depends(
        Provide[ApplicationContainer.suggest_game_service]
    ),
) -> Dict[str, str]:
    """Suggests good game"""
    suggested_game = await suggest_game_service.suggest()
    return {"game": suggested_game}
