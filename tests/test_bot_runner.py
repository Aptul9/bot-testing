"""Generic runner tests in bots.base.Bot."""

from __future__ import annotations

import asyncio
import time

import pytest

from waf_bots.bots.base import Bot
from waf_bots.common.waf_signals import WafObservation, WafSignal


class _FixedSignalBot(Bot):
    """Test bot: emits observations with predefined signals at controlled rate."""

    name = "test-fixed"

    def __init__(
        self,
        *,
        duration_s: int,
        concurrency: int,
        signal_sequence: list[WafSignal],
        request_delay_s: float = 0.0,
        endpoint: str = "/test",
        rps_per_worker: float = 0.0,
    ) -> None:
        super().__init__(
            "https://example.invalid",
            duration_s,
            concurrency,
            rps_per_worker=rps_per_worker,
        )
        self._sequence = list(signal_sequence)
        self._idx_lock = asyncio.Lock()
        self._idx = 0
        self._delay = request_delay_s
        self._endpoint = endpoint

    async def issue_request(self, worker_id: int, sequence: int) -> WafObservation:
        if self._delay:
            await asyncio.sleep(self._delay)
        async with self._idx_lock:
            i = min(self._idx, len(self._sequence) - 1)
            self._idx += 1
        sig = self._sequence[i]
        return WafObservation(
            signal=sig,
            status_code=200 if sig is WafSignal.NONE else 403,
            location=None,
            elapsed_ms=1.0,
            endpoint=self._endpoint,
        )


@pytest.mark.asyncio
async def test_runner_aggregates_signals_and_first_block() -> None:
    sequence = [WafSignal.NONE, WafSignal.NONE, WafSignal.BLOCKED_403, WafSignal.NONE]
    bot = _FixedSignalBot(
        duration_s=1,
        concurrency=1,
        signal_sequence=sequence,
        request_delay_s=0.05,
    )
    report = await bot.run()
    assert report.bot == "test-fixed"
    assert report.requests_total >= 3
    assert report.first_block_after_requests is not None
    assert report.first_block_after_s is not None
    assert report.first_block_after_s > 0
    assert report.signals_count.get("blocked_403", 0) >= 1


@pytest.mark.asyncio
async def test_runner_no_block_signal_keeps_first_block_none() -> None:
    bot = _FixedSignalBot(
        duration_s=1,
        concurrency=1,
        signal_sequence=[WafSignal.NONE],
        request_delay_s=0.05,
    )
    report = await bot.run()
    assert report.first_block_after_s is None
    assert report.first_block_after_requests is None
    assert report.signals_count.get("none", 0) >= 1


@pytest.mark.asyncio
async def test_runner_concurrency_runs_multiple_workers() -> None:
    bot = _FixedSignalBot(
        duration_s=1,
        concurrency=3,
        signal_sequence=[WafSignal.NONE],
        request_delay_s=0.1,
    )
    report = await bot.run()
    assert report.metadata["concurrency"] == 3
    assert report.requests_total >= 3


@pytest.mark.asyncio
async def test_runner_signals_by_endpoint_aggregates() -> None:
    sequence = [WafSignal.NONE, WafSignal.BLOCKED_403]
    bot = _FixedSignalBot(
        duration_s=1,
        concurrency=1,
        signal_sequence=sequence,
        request_delay_s=0.05,
        endpoint="/api/x",
    )
    report = await bot.run()
    assert "/api/x" in report.signals_by_endpoint
    bucket = report.signals_by_endpoint["/api/x"]
    assert bucket.get("blocked_403", 0) >= 1
    assert bucket.get("none", 0) >= 1


@pytest.mark.asyncio
async def test_runner_rps_caps_request_rate() -> None:
    # 10 RPS per worker, 1 worker, 1s duration => around 10 requests
    bot = _FixedSignalBot(
        duration_s=1,
        concurrency=1,
        signal_sequence=[WafSignal.NONE],
        rps_per_worker=10.0,
    )
    start = time.monotonic()
    report = await bot.run()
    elapsed = time.monotonic() - start
    assert elapsed >= 1.0
    # tolerate scheduler jitter; should be close to 10
    assert 5 <= report.requests_total <= 15
    assert report.metadata["rps_per_worker"] == 10.0


@pytest.mark.asyncio
async def test_runner_rps_zero_means_unlimited() -> None:
    bot = _FixedSignalBot(
        duration_s=1,
        concurrency=1,
        signal_sequence=[WafSignal.NONE],
        rps_per_worker=0.0,
        request_delay_s=0.001,
    )
    report = await bot.run()
    # without rate cap and with tiny per-request delay, we should observe many requests
    assert report.requests_total >= 50
