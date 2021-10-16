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
from bgd.responses import GameDetailsResult, GameSearchResult, Price
from bgd.services import BoardGameGeekService, DataSource

router = APIRouter()

TEST_RESULTS = [
    {
        "description": "",
        "images": [
            "https://yams.kufar.by/api/v1/kufar-ads/images/93/9362774727.jpg?rule=gallery",
            "https://yams.kufar.by/api/v1/kufar-ads/images/93/9345728089.jpg?rule=gallery",
            "https://yams.kufar.by/api/v1/kufar-ads/images/93/9379821365.jpg?rule=gallery",
            "https://yams.kufar.by/api/v1/kufar-ads/images/93/9354251408.jpg?rule=gallery",
            "https://yams.kufar.by/api/v1/kufar-ads/images/11/1165642781.jpg?rule=gallery",
        ],
        "location": {
            "area": "\u0424\u0440\u0443\u043d\u0437\u0435\u043d\u0441\u043a\u0438\u0439",
            "city": "\u041c\u0438\u043d\u0441\u043a",
            "country": "Belarus",
        },
        "owner": {
            "id": "6087223",
            "name": "\u0410\u043b\u0435\u043a\u0441\u0435\u0439 ",
        },
        "price": Price(byn=15000, usd=6119),
        "source": "kufar",
        "subject": "\u041d\u0430\u0441\u0442\u043e\u043b\u044c\u043d\u044b\u0435 \u0438\u0433\u0440\u044b ",
        "url": "https://www.kufar.by/item/137152905",
    },
    {
        "description": "",
        "images": [
            "https://yams.kufar.by/api/v1/kufar-ads/images/00/0051877366.jpg?rule=gallery",
            "https://yams.kufar.by/api/v1/kufar-ads/images/00/0047073440.jpg?rule=gallery",
            "https://yams.kufar.by/api/v1/kufar-ads/images/00/0030026802.jpg?rule=gallery",
            "https://yams.kufar.by/api/v1/kufar-ads/images/00/0012980164.jpg?rule=gallery",
            "https://yams.kufar.by/api/v1/kufar-ads/images/09/0904235265.jpg?rule=gallery",
        ],
        "location": {
            "area": "\u041c\u043e\u0441\u043a\u043e\u0432\u0441\u043a\u0438\u0439",
            "city": "\u041c\u0438\u043d\u0441\u043a",
            "country": "Belarus",
        },
        "owner": {"id": "1485628", "name": "\u0421\u0435\u0440\u0433\u0435\u0439"},
        "price": Price(byn=17000, usd=6935),
        "source": "kufar",
        "subject": "Eclipse \u0431\u0430\u0437\u0430 \u0438/\u0438\u043b\u0438 \u0434\u043e\u043f Rise of the Antients",
        "url": "https://www.kufar.by/item/121425226",
    },
]

TEST_INFO = {
    "description": "The galaxy has been a peaceful place for many years. After the ruthless Terran&ndash;Hegemony War (30.027&ndash;33.364), much effort has been employed by all major spacefaring species to prevent the terrifying events from repeating themselves. The Galactic Council was formed to enforce precious peace, and it has taken many courageous efforts to prevent the escalation of malicious acts. Nevertheless, tension and discord are growing among the seven major species and in the Council itself. Old alliances are shattering, and hasty diplomatic treaties are made in secrecy. A confrontation of the superpowers seems inevitable &ndash; only the outcome of the galactic conflict remains to be seen. Which faction will emerge victorious and lead the galaxy under its rule?&#10;&#10;A game of Eclipse places you in control of a vast interstellar civilization, competing for success with its rivals. You will explore new star systems, research technologies, and build spaceships with which to wage war. There are many potential paths to victory, so you need to plan your strategy according to the strengths and weaknesses of your species, while paying attention to the other civilizations' endeavors.&#10;&#10;The shadows of the great civilizations are about to eclipse the galaxy. Lead your people to victory!&#10;&#10;",
    "id": "72125",
    "image": "https://cf.geekdo-images.com/cnFppsVNOSTJ-W3APQFuTg__original/img/AbcjscBi-x3tVrsJsBhXq2RxLbc=/0x0/filters:format(jpeg)/pic1974056.jpg",
    "max_play_time": "180",
    "max_players": "6",
    "min_play_time": "60",
    "min_players": "2",
    "name": "Eclipse",
    "playing_time": "180",
    "statistics": {
        "avg_rate": "7.88082",
        "ranks": [
            {"name": "boardgame", "value": "58"},
            {"name": "strategygames", "value": "52"},
        ],
        "weight": "3.7002",
    },
    "url": "https://boardgamegeek.com/boardgame/72125",
    "year_published": "2011",
}


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
    # results = await search_game(name)
    # game_info = await game_details(name)
    results = TEST_RESULTS
    game_info = TEST_INFO
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "name": name,
            "results": results,
            "game_info": game_info,
        },
    )
