"""Factory per client httpx async usato dai BOT HTTP-only."""

from __future__ import annotations

import httpx

DEFAULT_TIMEOUT = httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=10.0)
DEFAULT_USER_AGENT = "waf-bots/0.1 (intentional-bot)"


def create_client(
    base_url: str,
    *,
    user_agent: str = DEFAULT_USER_AGENT,
    verify: bool = True,
    http2: bool = True,
) -> httpx.AsyncClient:
    """Crea un client httpx async preconfigurato.

    I default rendono il client palesemente riconoscibile come bot:
    User-Agent esplicito, nessuna rotazione di header o fingerprint,
    nessun follow_redirects (necessario per intercettare challenge WAF).
    """
    headers = {"User-Agent": user_agent}
    return httpx.AsyncClient(
        base_url=base_url,
        headers=headers,
        timeout=DEFAULT_TIMEOUT,
        verify=verify,
        http2=http2,
        follow_redirects=False,
    )
