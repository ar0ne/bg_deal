"""
App containers
"""
from dependency_injector import containers, providers

from bgd import services
from bgd.clients import KufarApiClient


class ApplicationContainer(containers.DeclarativeContainer):
    """App container"""

    config = providers.Configuration()

    kufar_api_client = providers.Factory(
        KufarApiClient,
    )

    kufar_search_service = providers.Factory(
        services.KufarSearchService,
        client=kufar_api_client,
    )
