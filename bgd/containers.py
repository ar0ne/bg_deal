"""
App containers
"""
import os

from dependency_injector import containers, providers
from starlette.templating import Jinja2Templates

from bgd.clients import services
from bgd.clients.builders import (
    BGGGameDetailsResultBuilder,
    GameSearchResultFifthElementBuilder,
    GameSearchResultKufarBuilder,
    GameSearchResultOnlinerBuilder,
    GameSearchResultOzByBuilder,
    GameSearchResultOzonBuilder,
    GameSearchResultTwentyFirstVekBuilder,
    GameSearchResultVkontakteBuilder,
    GameSearchResultWildberriesBuilder,
    TeseraGameDetailsResultBuilder,
)
from bgd.clients.clients import (
    BoardGameGeekApiClient,
    FifthElementApiClient,
    KufarApiClient,
    OnlinerApiClient,
    OzByApiClient,
    OzonApiClient,
    TeseraApiClient,
    TwentyFirstVekApiClient,
    VkontakteApiClient,
    WildberriesApiClient,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# pylint: disable=I1101
class ApplicationContainer(containers.DeclarativeContainer):
    """App container"""

    config = providers.Configuration()

    templates = providers.Factory(
        Jinja2Templates,
        directory=config.templates.dir,
    )

    bgg_api_client = providers.Factory(
        BoardGameGeekApiClient,
    )
    bgg_service = providers.Factory(
        services.BoardGameGeekGameInfoService,
        client=bgg_api_client,
        builder=BGGGameDetailsResultBuilder,
    )

    tesera_api_client = providers.Factory(
        TeseraApiClient,
    )
    tesera_service = providers.Factory(
        services.TeseraGameInfoService,
        client=tesera_api_client,
        builder=TeseraGameDetailsResultBuilder,
    )

    kufar_api_client = providers.Factory(
        KufarApiClient,
    )
    kufar_search_service = providers.Factory(
        services.KufarSearchService,
        client=kufar_api_client,
        game_category_id=config.kufar.game_category_id,
        result_builder=GameSearchResultKufarBuilder,
    )

    wildberries_api_client = providers.Factory(
        WildberriesApiClient,
    )
    wildberreis_search_service = providers.Factory(
        services.WildberriesSearchService,
        client=wildberries_api_client,
        game_category_id=config.wildberries.game_category_id,
        result_builder=GameSearchResultWildberriesBuilder,
    )

    ozon_api_client = providers.Factory(
        OzonApiClient,
    )
    ozon_search_service = providers.Factory(
        services.OzonSearchService,
        client=ozon_api_client,
        game_category_id=config.ozon.game_category_id,
        result_builder=GameSearchResultOzonBuilder,
    )

    ozby_api_client = providers.Factory(
        OzByApiClient,
    )
    ozby_search_service = providers.Factory(
        services.OzBySearchService,
        client=ozby_api_client,
        game_category_id=config.ozby.game_category_id,
        result_builder=GameSearchResultOzByBuilder,
    )

    onliner_api_client = providers.Factory(
        OnlinerApiClient,
    )
    onliner_search_service = providers.Factory(
        services.OnlinerSearchService,
        client=onliner_api_client,
        game_category_id="",
        result_builder=GameSearchResultOnlinerBuilder,
    )

    twenty_first_vek_api_client = providers.Factory(
        TwentyFirstVekApiClient,
    )
    twenty_first_vek_service = providers.Factory(
        services.TwentyFirstVekSearchService,
        client=twenty_first_vek_api_client,
        game_category_id="",
        result_builder=GameSearchResultTwentyFirstVekBuilder,
    )

    fifth_element_api_client = providers.Factory(
        FifthElementApiClient,
    )
    fifth_element_service = providers.Factory(
        services.FifthElementSearchService,
        client=fifth_element_api_client,
        game_category_id=config.fifthelement.game_category_id,
        search_app_id=config.fifthelement.search_app_id,
        result_builder=GameSearchResultFifthElementBuilder,
    )

    vk_api_client = providers.Factory(
        VkontakteApiClient,
    )
    vk_service = providers.Factory(
        services.VkontakteSearchService,
        client=vk_api_client,
        game_category_id="",
        group_id=config.vk.group_id,
        group_name=config.vk.group_name,
        api_token=config.vk.api_token,
        api_version=config.vk.api_version,
        limit=config.vk.limit,
        result_builder=GameSearchResultVkontakteBuilder,
    )

    data_sources = providers.List(
        kufar_search_service,
        wildberreis_search_service,
        ozon_search_service,
        ozby_search_service,
        onliner_search_service,
        twenty_first_vek_service,
        fifth_element_service,
        vk_service,
    )

    suggest_game_service = providers.Factory(
        services.SuggestGameService,
        games=config.app.suggested_games,
    )
