"""Unit test sul classificatore di segnali WAF."""

from __future__ import annotations

import pytest

from waf_bots.common.waf_signals import WafSignal, classify


@pytest.mark.parametrize(
    ("status", "location", "expected"),
    [
        (200, None, WafSignal.NONE),
        (403, None, WafSignal.BLOCKED_403),
        (429, None, WafSignal.RATE_LIMITED_429),
        (503, None, WafSignal.SERVICE_UNAVAILABLE_503),
        (302, "https://waf.example/challenge", WafSignal.CHALLENGE_REDIRECT),
        (302, "https://example.com/captcha-page", WafSignal.CHALLENGE_REDIRECT),
        (302, "https://example.com/ok", WafSignal.NONE),
        (None, None, WafSignal.NONE),
    ],
)
def test_classify(status: int | None, location: str | None, expected: WafSignal) -> None:
    assert classify(status, location) is expected
