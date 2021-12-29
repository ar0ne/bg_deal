"""
National Bank (nb.by) API Client
"""
import datetime

from bgd.services.constants import GET
from bgd.services.protocols import XmlHttpApiClient
from bgd.services.responses import APIResponse


class NationalBankApiClient(XmlHttpApiClient):
    """API client for Belarus national bank"""

    BASE_URL = "https://www.nbrb.by"
    EXCHANGE_RATE_PATH = "/services/xmlexrates.aspx"

    async def get_currency_exchange_rates(self, on_date: datetime.date) -> APIResponse:
        """
        Get currency exchange rates at date.
        :param date on_date: Date for which we need currency exchange rates.
        """
        formatted_date = on_date.strftime("%m/%d/%Y")
        url = f"{self.EXCHANGE_RATE_PATH}?ondate={formatted_date}"
        return await self.connect(GET, self.BASE_URL, url)
