"""Test su observe_response e observe_exception."""

from __future__ import annotations

import httpx
import pytest

from waf_bots.common.http import observe_exception, observe_response
from waf_bots.common.waf_signals import WafSignal


def _build_response(status: int, headers: dict[str, str] | None = None) -> httpx.Response:
    return httpx.Response(status_code=status, headers=headers or {})


def test_observe_response_200_none() -> None:
    obs = observe_response(_build_response(200), elapsed_ms=12.5)
    assert obs.signal is WafSignal.NONE
    assert obs.status_code == 200
    assert obs.location is None


def test_observe_response_403_blocked() -> None:
    obs = observe_response(_build_response(403), elapsed_ms=4.0)
    assert obs.signal is WafSignal.BLOCKED_403


def test_observe_response_429_rate_limited() -> None:
    obs = observe_response(_build_response(429), elapsed_ms=3.0)
    assert obs.signal is WafSignal.RATE_LIMITED_429


def test_observe_response_503_unavailable() -> None:
    obs = observe_response(_build_response(503), elapsed_ms=2.0)
    assert obs.signal is WafSignal.SERVICE_UNAVAILABLE_503


def test_observe_response_redirect_to_challenge() -> None:
    resp = _build_response(302, {"location": "https://x.example/challenge"})
    obs = observe_response(resp, elapsed_ms=1.0)
    assert obs.signal is WafSignal.CHALLENGE_REDIRECT
    assert obs.location == "https://x.example/challenge"


def test_observe_response_redirect_benign() -> None:
    resp = _build_response(302, {"location": "https://x.example/dashboard"})
    obs = observe_response(resp, elapsed_ms=1.0)
    assert obs.signal is WafSignal.NONE


@pytest.mark.parametrize(
    ("exc", "expected"),
    [
        (httpx.ConnectTimeout("connect"), WafSignal.TIMEOUT),
        (httpx.ReadTimeout("read"), WafSignal.TIMEOUT),
        (httpx.PoolTimeout("pool"), WafSignal.TIMEOUT),
        (httpx.ConnectError("conn refused"), WafSignal.CONNECTION_RESET),
        (httpx.ReadError("read err"), WafSignal.CONNECTION_RESET),
        (httpx.RemoteProtocolError("proto"), WafSignal.CONNECTION_RESET),
        (RuntimeError("unrelated"), WafSignal.NONE),
    ],
)
def test_observe_exception(exc: BaseException, expected: WafSignal) -> None:
    obs = observe_exception(exc, elapsed_ms=5.0)
    assert obs.signal is expected
    assert obs.status_code is None
