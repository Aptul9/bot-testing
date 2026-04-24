"""Factory Playwright Chromium per i BOT browser-based."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from playwright.async_api import Browser, BrowserContext, Playwright, async_playwright


@asynccontextmanager
async def launch_browser(
    *,
    headless: bool = True,
    user_agent: str | None = None,
) -> AsyncIterator[tuple[Playwright, Browser, BrowserContext]]:
    """Apre Playwright + Chromium headless senza stealth.

    Default deliberatamente riconoscibili come automation, allineati all'obiettivo
    del test antiBot: navigator.webdriver=true (default Playwright, non mascherato),
    nessun stealth plugin, nessuna rotazione fingerprint.
    """
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        context = await browser.new_context(user_agent=user_agent)
        try:
            yield pw, browser, context
        finally:
            await context.close()
            await browser.close()
