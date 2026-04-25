"""BOT-5 Price Scraping. Target: catalogo offerte e zone."""

from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar

from waf_bots.bots.browser_bot import BrowserBot

API_PREFIX = "/smnadarte-integration-app-web/app/api"

# Placeholder per parametri path. Il backend potra' rispondere 404 o 400 ma
# l'obiettivo e' il pattern di richieste ripetute, non la validita' funzionale.
ZONE_CODESR_PLACEHOLDER = "WAFTEST"
ZONE_ID_PLACEHOLDER = "1"


class PriceScrapingBot(BrowserBot):
    name = "bot-5-price-scraping"

    paths: ClassVar[Sequence[str]] = (
        f"{API_PREFIX}/offer/availability",
        f"{API_PREFIX}/offer/timeslot",
        f"{API_PREFIX}/zone/codesr/{ZONE_CODESR_PLACEHOLDER}",
        f"{API_PREFIX}/zone/{ZONE_ID_PLACEHOLDER}",
    )
