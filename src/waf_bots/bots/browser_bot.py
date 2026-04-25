"""Classe base per i BOT browser-based (Playwright)."""

from __future__ import annotations

import time
from collections.abc import Sequence
from typing import ClassVar
from urllib.parse import urljoin

from playwright.async_api import (
    Browser,
    BrowserContext,
    Playwright,
    async_playwright,
)
from playwright.async_api import (
    Error as PlaywrightError,
)
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
)

from waf_bots.bots.base import Bot
from waf_bots.common.waf_signals import WafObservation, WafSignal, classify

NAV_TIMEOUT_MS = 15_000


class BrowserBot(Bot):
    """Bot che naviga con Chromium headless di Playwright.

    Configurazione deliberatamente palese (no stealth, no UA spoofing,
    `navigator.webdriver=true` di default). I BOT concreti definiscono
    `paths`: una sequenza di path relativi al `base_url` su cui ciclare.
    """

    paths: ClassVar[Sequence[str]] = ()

    def __init__(
        self,
        base_url: str,
        duration_s: int,
        concurrency: int = 1,
        *,
        dry_run: bool = True,
    ) -> None:
        super().__init__(base_url, duration_s, concurrency, dry_run=dry_run)
        if not self.paths:
            raise ValueError(f"{type(self).__name__}.paths non puo' essere vuoto")
        self._pw: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    async def setup(self) -> None:
        if self.dry_run:
            return
        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=True)
        self._context = await self._browser.new_context()

    async def teardown(self) -> None:
        if self._context is not None:
            await self._context.close()
            self._context = None
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
        if self._pw is not None:
            await self._pw.stop()
            self._pw = None

    def _next_url(self, sequence: int) -> str:
        path = self.paths[(sequence - 1) % len(self.paths)]
        if not self.base_url.endswith("/") and not path.startswith("/"):
            return f"{self.base_url}/{path}"
        return urljoin(
            self.base_url + ("" if self.base_url.endswith("/") else "/"), path.lstrip("/")
        )

    async def issue_request(self, worker_id: int, sequence: int) -> WafObservation:
        if self.dry_run:
            # Dry-run: nessuna navigazione reale, restituisco osservazione neutra.
            return WafObservation(WafSignal.NONE, None, None, 0.0)
        if self._context is None:
            raise RuntimeError(
                "BrowserBot.setup() non eseguito (dry_run=False richiede Playwright)"
            )
        url = self._next_url(sequence)
        page = await self._context.new_page()
        start = time.monotonic()
        try:
            try:
                response = await page.goto(
                    url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS
                )
            except PlaywrightTimeoutError:
                elapsed_ms = (time.monotonic() - start) * 1000
                return WafObservation(WafSignal.TIMEOUT, None, None, elapsed_ms)
            except PlaywrightError:
                elapsed_ms = (time.monotonic() - start) * 1000
                return WafObservation(WafSignal.CONNECTION_RESET, None, None, elapsed_ms)

            elapsed_ms = (time.monotonic() - start) * 1000
            if response is None:
                return WafObservation(WafSignal.NONE, None, None, elapsed_ms)
            location = (
                response.headers.get("location")
                if response.status in (301, 302, 303, 307, 308)
                else None
            )
            return WafObservation(
                signal=classify(response.status, location),
                status_code=response.status,
                location=location,
                elapsed_ms=elapsed_ms,
            )
        finally:
            await page.close()
