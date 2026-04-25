"""BOT-4 Content Scraping. Target: pagine di navigazione su prenotazioni QR."""

from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar

from waf_bots.bots.browser_bot import BrowserBot

# Placeholder QR code per test antiBot. Il backend rispondera' 404 o errore;
# il WAF rileva comunque il pattern di scraping ripetuto sui medesimi path.
QR_PLACEHOLDER = "WAFTEST00000001"

API_PREFIX = "/smnadarte-integration-app-web/app/api"


class ContentScrapingBot(BrowserBot):
    name = "bot-4-content-scraping"

    paths: ClassVar[Sequence[str]] = (
        f"{API_PREFIX}/reservation/access/{QR_PLACEHOLDER}",
        f"{API_PREFIX}/reservation/for/{QR_PLACEHOLDER}",
        f"{API_PREFIX}/reservation/zone/{QR_PLACEHOLDER}",
    )
