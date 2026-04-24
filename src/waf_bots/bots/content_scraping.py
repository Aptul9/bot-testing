"""BOT-4 Content Scraping. Target: pagine di navigazione."""

from __future__ import annotations

from waf_bots.bots.base import Bot
from waf_bots.common.reporter import RunReport


class ContentScrapingBot(Bot):
    name = "bot-4-content-scraping"

    async def run(self) -> RunReport:
        raise NotImplementedError("BOT-4 non ancora implementato")
