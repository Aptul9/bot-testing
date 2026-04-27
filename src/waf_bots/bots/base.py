"""Bot base class and generic runner."""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime

from waf_bots.common.logger import get_logger
from waf_bots.common.reporter import RunReport
from waf_bots.common.waf_signals import WafObservation, is_block_signal


class Bot(ABC):
    """Common BOT contract.

    The generic runner (`run`) handles the timed loop, concurrency, observation
    collection, first-block tracking and `RunReport` aggregation. Concrete BOTs
    implement `setup`, `teardown`, `issue_request`.
    """

    name: str

    def __init__(
        self,
        base_url: str,
        duration_s: int,
        concurrency: int = 1,
        *,
        dry_run: bool = True,
        rps_per_worker: float = 0.0,
    ) -> None:
        self.base_url = base_url
        self.duration_s = duration_s
        self.concurrency = max(1, concurrency)
        self.dry_run = dry_run
        # rps_per_worker = 0 means no rate limiting. Aggregate target RPS =
        # rps_per_worker * concurrency.
        self.rps_per_worker = max(0.0, rps_per_worker)
        self._log = get_logger(f"waf_bots.runner.{self.name}")

    async def setup(self) -> None:  # noqa: B027 - template method, override optional
        """Pre-loop init. Default: no-op."""

    async def teardown(self) -> None:  # noqa: B027 - template method, override optional
        """Post-loop cleanup. Default: no-op."""

    @abstractmethod
    async def issue_request(self, worker_id: int, sequence: int) -> WafObservation:
        """Single interaction with the target. Returns the observation.

        Implementations should populate `WafObservation.endpoint` so the
        reporter can break signals down per endpoint.
        """

    async def run(self) -> RunReport:
        await self.setup()
        try:
            return await self._run_loop()
        finally:
            await self.teardown()

    async def _run_loop(self) -> RunReport:
        report = RunReport.new(self.name)
        report.metadata.update(
            base_url=self.base_url,
            duration_s=self.duration_s,
            concurrency=self.concurrency,
            dry_run=self.dry_run,
            rps_per_worker=self.rps_per_worker,
        )

        self._log.info(
            "run_start",
            extra={
                "extra_fields": {
                    "bot": self.name,
                    "base_url": self.base_url,
                    "duration_s": self.duration_s,
                    "concurrency": self.concurrency,
                    "dry_run": self.dry_run,
                    "rps_per_worker": self.rps_per_worker,
                }
            },
        )

        start = time.monotonic()
        deadline = start + self.duration_s
        lock = asyncio.Lock()
        observations: list[WafObservation] = []
        first_block_t: float | None = None
        first_block_idx: int | None = None
        period = 1.0 / self.rps_per_worker if self.rps_per_worker > 0 else 0.0

        async def worker(worker_id: int) -> None:
            nonlocal first_block_t, first_block_idx
            sequence = 0
            next_send = time.monotonic()
            while time.monotonic() < deadline:
                if period:
                    sleep_for = next_send - time.monotonic()
                    if sleep_for > 0:
                        await asyncio.sleep(sleep_for)
                    next_send += period
                sequence += 1
                obs = await self.issue_request(worker_id=worker_id, sequence=sequence)
                async with lock:
                    observations.append(obs)
                    idx = len(observations)
                    if first_block_idx is None and is_block_signal(obs.signal):
                        first_block_idx = idx
                        first_block_t = time.monotonic() - start
                        self._log.warning(
                            "first_block",
                            extra={
                                "extra_fields": {
                                    "bot": self.name,
                                    "after_s": round(first_block_t, 3),
                                    "after_requests": idx,
                                    "signal": obs.signal.value,
                                    "status_code": obs.status_code,
                                    "endpoint": obs.endpoint,
                                }
                            },
                        )
                    elif is_block_signal(obs.signal):
                        # Subsequent block events; logged at debug-level via info
                        # to keep volume sensible without flooding for NONE.
                        self._log.info(
                            "block_event",
                            extra={
                                "extra_fields": {
                                    "bot": self.name,
                                    "worker_id": worker_id,
                                    "sequence": sequence,
                                    "signal": obs.signal.value,
                                    "status_code": obs.status_code,
                                    "endpoint": obs.endpoint,
                                }
                            },
                        )

        await asyncio.gather(*(worker(i) for i in range(self.concurrency)))

        elapsed = time.monotonic() - start
        signals_count: dict[str, int] = {}
        signals_by_endpoint: dict[str, dict[str, int]] = {}
        for obs in observations:
            key = obs.signal.value
            signals_count[key] = signals_count.get(key, 0) + 1
            ep = obs.endpoint or "<unknown>"
            ep_bucket = signals_by_endpoint.setdefault(ep, {})
            ep_bucket[key] = ep_bucket.get(key, 0) + 1

        report.duration_s = round(elapsed, 3)
        report.requests_total = len(observations)
        report.first_block_after_s = round(first_block_t, 3) if first_block_t is not None else None
        report.first_block_after_requests = first_block_idx
        report.signals_count = signals_count
        report.signals_by_endpoint = signals_by_endpoint
        report.ended_at = datetime.now(tz=UTC).isoformat()

        self._log.info(
            "run_end",
            extra={
                "extra_fields": {
                    "bot": self.name,
                    "duration_s": report.duration_s,
                    "requests_total": report.requests_total,
                    "first_block_after_s": report.first_block_after_s,
                    "first_block_after_requests": report.first_block_after_requests,
                    "signals_count": signals_count,
                }
            },
        )
        return report
