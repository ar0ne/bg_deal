"""
VKontakte (vk.com) API Client
"""
from typing import Optional

from bgd.api_clients.constants import GET
from bgd.api_clients.protocols import JsonHttpApiClient
from bgd.api_clients.responses import APIResponse


class VkontakteApiClient(JsonHttpApiClient):
    """Api client for vk.com"""

    BASE_URL = "https://api.vk.com/method"

    async def search(self, _: str, options: Optional[dict] = None) -> APIResponse:
        """Search query on group wall"""
        options = options or {}
        group_id = f"-{options['group_id']}"
        url = (
            f"/wall.get"
            f"?owner_id={group_id}"
            f"&v={options['api_version']}"
            f"&count={options['limit']}"
            f"&access_token={options['api_token']}"
        )
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        return await self.connect(GET, self.BASE_URL, url, headers=headers)
