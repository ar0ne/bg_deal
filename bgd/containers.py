"""
App containers
"""
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    """App container"""

    config = providers.Configuration()

    # todo: add injecting services
