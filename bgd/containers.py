"""
App containers
"""
from dependency_injector import containers, providers

from bgd import services
from bgd.clients import KufarApiClient, OzonApiClient, WildberriesApiClient


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
    )

    wildberries_api_client = providers.Factory(
        WildberriesApiClient,
    )
    wildberreis_search_service = providers.Factory(
        services.WildberriesSearchService,
        client=wildberries_api_client,
        game_category_id=config.wildberries.game_category_id,
    )

    ozon_api_client = providers.Factory(
        OzonApiClient,
    )
    ozon_search_service = providers.Factory(
        services.OzonSearchService,
        client=ozon_api_client,
        game_category_id=config.ozon.game_category_id,
    )

    data_sources = providers.List(
        ozon_search_service,
        # kufar_search_service,
        # wildberreis_search_service,
    )
