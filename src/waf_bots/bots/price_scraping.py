"""BOT-5 Price Scraping. Target: catalogo prodotti/offerte."""

from __future__ import annotations

from waf_bots.bots.base import Bot
from waf_bots.common.reporter import RunReport


class PriceScrapingBot(Bot):
    name = "bot-5-price-scraping"

    async def run(self) -> RunReport:
        raise NotImplementedError("BOT-5 non ancora implementato")
