"""BOT-4 Content Scraping. Target: pagine di navigazione."""

from __future__ import annotations

from waf_bots.bots.base import Bot
from waf_bots.common.waf_signals import WafObservation


class ContentScrapingBot(Bot):
    name = "bot-4-content-scraping"

    async def issue_request(self, worker_id: int, sequence: int) -> WafObservation:
        raise NotImplementedError("BOT-4 non ancora implementato")
