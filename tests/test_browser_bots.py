"""Smoke test sui BOT browser-based (senza avviare Playwright)."""

from __future__ import annotations

import pytest

from waf_bots.bots.browser_bot import BrowserBot
from waf_bots.bots.content_scraping import ContentScrapingBot
from waf_bots.bots.price_scraping import PriceScrapingBot


def test_content_scraping_paths_non_empty() -> None:
    assert len(ContentScrapingBot.paths) >= 3
    for path in ContentScrapingBot.paths:
        assert path.startswith("/smnadarte-integration-app-web/app/api/reservation/")


def test_price_scraping_paths_non_empty() -> None:
    assert len(PriceScrapingBot.paths) >= 4
    for path in PriceScrapingBot.paths:
        assert path.startswith("/smnadarte-integration-app-web/app/api/")


def test_browser_bot_url_building_with_trailing_slash() -> None:
    bot = ContentScrapingBot(
        base_url="https://api-coll.museiitaliani.it",
        duration_s=1,
        concurrency=1,
    )
    url = bot._next_url(1)
    assert url.startswith("https://api-coll.museiitaliani.it/")
    assert "reservation/access" in url


def test_browser_bot_url_cycles_through_paths() -> None:
    bot = PriceScrapingBot(
        base_url="https://api-coll.museiitaliani.it",
        duration_s=1,
        concurrency=1,
    )
    urls = {bot._next_url(i) for i in range(1, len(PriceScrapingBot.paths) + 1)}
    assert len(urls) == len(PriceScrapingBot.paths)


def test_browser_bot_rejects_empty_paths() -> None:
    class EmptyBot(BrowserBot):
        name = "empty"

    with pytest.raises(ValueError, match="paths"):
        EmptyBot(base_url="https://x.invalid", duration_s=1)


def test_no_overlap_content_vs_price() -> None:
    overlap = set(ContentScrapingBot.paths) & set(PriceScrapingBot.paths)
    assert overlap == set()
