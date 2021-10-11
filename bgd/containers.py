"""
App containers
"""
from dependency_injector import containers, providers

from bgd import services
from bgd.builders import (
    GameSearchResultKufarBuilder,
    GameSearchResultOzonBuilder,
    GameSearchResultWildberriesBuilder,
)
from bgd.clients import (
    BoardGameGeekApiClient,
    KufarApiClient,
    OzonApiClient,
    WildberriesApiClient,
)


class ApplicationContainer(containers.DeclarativeContainer):
    """App container"""

    config = providers.Configuration()

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

    data_sources = providers.List(
        kufar_search_service,
        wildberreis_search_service,
        ozon_search_service,
    )

    bgg_api_client = providers.Factory(
        BoardGameGeekApiClient,
    )
    bgg_service = providers.Factory(
        services.BoardGameGeekService,
        client=bgg_api_client,
    )
