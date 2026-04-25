"""Classe base e runner generico per i BOT."""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime

from waf_bots.common.reporter import RunReport
from waf_bots.common.waf_signals import WafObservation, is_block_signal


class Bot(ABC):
    """Contratto comune dei BOT.

    Il runner generico (`run`) gestisce loop temporale, concorrenza, raccolta
    osservazioni e aggregazione nel `RunReport`. I BOT concreti implementano
    `setup`/`teardown` e `issue_request` per la singola interazione col target.
    """

    name: str

    def __init__(
        self,
        base_url: str,
        duration_s: int,
        concurrency: int = 1,
        *,
        dry_run: bool = True,
    ) -> None:
        self.base_url = base_url
        self.duration_s = duration_s
        self.concurrency = max(1, concurrency)
        self.dry_run = dry_run

    async def setup(self) -> None:  # noqa: B027 - template method, override opzionale
        """Inizializzazione prima del loop. Default: no-op."""

    async def teardown(self) -> None:  # noqa: B027 - template method, override opzionale
        """Cleanup post loop. Default: no-op."""

    @abstractmethod
    async def issue_request(self, worker_id: int, sequence: int) -> WafObservation:
        """Esegue una singola interazione col target e restituisce l'osservazione.

        Le eccezioni non gestite dall'implementazione vengono catturate dal
        runner e classificate come WafObservation con segnale NONE.
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
        )

        start = time.monotonic()
        deadline = start + self.duration_s
        lock = asyncio.Lock()
        observations: list[WafObservation] = []
        first_block_t: float | None = None
        first_block_idx: int | None = None

        async def worker(worker_id: int) -> None:
            nonlocal first_block_t, first_block_idx
            sequence = 0
            while time.monotonic() < deadline:
                sequence += 1
                obs = await self.issue_request(worker_id=worker_id, sequence=sequence)
                async with lock:
                    observations.append(obs)
                    idx = len(observations)
                    if first_block_idx is None and is_block_signal(obs.signal):
                        first_block_idx = idx
                        first_block_t = time.monotonic() - start

        await asyncio.gather(*(worker(i) for i in range(self.concurrency)))

        elapsed = time.monotonic() - start
        signals_count: dict[str, int] = {}
        for obs in observations:
            key = obs.signal.value
            signals_count[key] = signals_count.get(key, 0) + 1

        report.duration_s = round(elapsed, 3)
        report.requests_total = len(observations)
        report.first_block_after_s = round(first_block_t, 3) if first_block_t is not None else None
        report.first_block_after_requests = first_block_idx
        report.signals_count = signals_count
        report.ended_at = datetime.now(tz=UTC).isoformat()
        return report
