"""Classificazione di segnali WAF osservabili lato client."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class WafSignal(StrEnum):
    NONE = "none"
    BLOCKED_403 = "blocked_403"
    RATE_LIMITED_429 = "rate_limited_429"
    SERVICE_UNAVAILABLE_503 = "service_unavailable_503"
    CONNECTION_RESET = "connection_reset"
    TIMEOUT = "timeout"
    CHALLENGE_REDIRECT = "challenge_redirect"


@dataclass(frozen=True)
class WafObservation:
    signal: WafSignal
    status_code: int | None
    location: str | None
    elapsed_ms: float


_CHALLENGE_TOKENS = ("challenge", "captcha", "block", "waf", "interstitial")


def classify(status_code: int | None, location: str | None) -> WafSignal:
    if status_code == 403:
        return WafSignal.BLOCKED_403
    if status_code == 429:
        return WafSignal.RATE_LIMITED_429
    if status_code == 503:
        return WafSignal.SERVICE_UNAVAILABLE_503
    if status_code in (301, 302, 303, 307, 308) and location:
        lower = location.lower()
        if any(token in lower for token in _CHALLENGE_TOKENS):
            return WafSignal.CHALLENGE_REDIRECT
    return WafSignal.NONE
