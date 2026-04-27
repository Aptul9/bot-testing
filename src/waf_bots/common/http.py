"""Factory and helpers for the httpx async client used by HTTP-only BOTs."""

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
    """Build a preconfigured httpx async client.

    Defaults make the client overtly bot-like: explicit User-Agent, no header
    rotation, no follow_redirects (so WAF challenge redirects are observable).
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


def observe_response(
    response: httpx.Response,
    elapsed_ms: float,
    *,
    endpoint: str | None = None,
) -> WafObservation:
    """Convert an httpx response into a WafObservation."""
    location = response.headers.get("location") if response.is_redirect else None
    return WafObservation(
        signal=classify(response.status_code, location),
        status_code=response.status_code,
        location=location,
        elapsed_ms=elapsed_ms,
        endpoint=endpoint,
    )


def observe_exception(
    exc: BaseException,
    elapsed_ms: float,
    *,
    endpoint: str | None = None,
) -> WafObservation:
    """Convert an httpx exception into a WafObservation.

    Connect/Read/RemoteProtocol -> CONNECTION_RESET.
    Timeout (any kind) -> TIMEOUT.
    Other exceptions -> NONE (not recognized as WAF signals).
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
        endpoint=endpoint,
    )
