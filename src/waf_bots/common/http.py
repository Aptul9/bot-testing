"""Factory e helper per client httpx async usato dai BOT HTTP-only."""

from __future__ import annotations

import httpx

from waf_bots.common.waf_signals import WafObservation, WafSignal, classify

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


def observe_response(response: httpx.Response, elapsed_ms: float) -> WafObservation:
    """Trasforma una risposta httpx in WafObservation."""
    location = response.headers.get("location") if response.is_redirect else None
    return WafObservation(
        signal=classify(response.status_code, location),
        status_code=response.status_code,
        location=location,
        elapsed_ms=elapsed_ms,
    )


def observe_exception(exc: BaseException, elapsed_ms: float) -> WafObservation:
    """Trasforma un'eccezione httpx in WafObservation.

    Connect/Read/RemoteProtocol -> CONNECTION_RESET.
    Timeout (qualsiasi tipo) -> TIMEOUT.
    Altre eccezioni -> NONE (non riconosciute come segnali WAF).
    """
    if isinstance(exc, httpx.TimeoutException):
        signal = WafSignal.TIMEOUT
    elif isinstance(exc, httpx.ConnectError | httpx.ReadError | httpx.RemoteProtocolError):
        signal = WafSignal.CONNECTION_RESET
    else:
        signal = WafSignal.NONE
    return WafObservation(
        signal=signal,
        status_code=None,
        location=None,
        elapsed_ms=elapsed_ms,
    )
