"""BOT-5 Price Scraping. Target: catalogo prodotti/offerte."""

from __future__ import annotations

from waf_bots.bots.base import Bot
from waf_bots.common.waf_signals import WafObservation


class PriceScrapingBot(Bot):
    name = "bot-5-price-scraping"

    async def issue_request(self, worker_id: int, sequence: int) -> WafObservation:
        raise NotImplementedError("BOT-5 non ancora implementato")
