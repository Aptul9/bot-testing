"""Classe base per i BOT HTTP-only (httpx async)."""

from __future__ import annotations

import time
from collections.abc import Mapping, Sequence
from typing import ClassVar

import httpx

from waf_bots.bots.base import Bot
from waf_bots.common.http import create_client, observe_exception, observe_response
from waf_bots.common.waf_signals import WafObservation, WafSignal


class HttpRequestSpec:
    """Descrittore di una singola richiesta che il BOT puo' emettere."""

    __slots__ = ("data", "headers", "json_body", "method", "path")

    def __init__(
        self,
        method: str,
        path: str,
        *,
        json_body: object = None,
        data: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self.method = method.upper()
        self.path = path
        self.json_body = json_body
        self.data = dict(data) if data is not None else None
        self.headers = dict(headers) if headers is not None else None


class HttpBot(Bot):
    """Bot HTTP-only.

    I BOT concreti definiscono una sequenza di `HttpRequestSpec` in `requests`.
    In modalita' `dry_run` (default) non viene aperto il client e nessuna richiesta
    viene effettivamente inviata: si emettono `WafObservation` sintetiche con
    `signal=NONE`, utili per la pipeline di sviluppo.
    """

    requests: ClassVar[Sequence[HttpRequestSpec]] = ()

    def __init__(
        self,
        base_url: str,
        duration_s: int,
        concurrency: int = 1,
        *,
        dry_run: bool = True,
        rps_per_worker: float = 0.0,
    ) -> None:
        super().__init__(
            base_url,
            duration_s,
            concurrency,
            dry_run=dry_run,
            rps_per_worker=rps_per_worker,
        )
        if not self.requests:
            raise ValueError(f"{type(self).__name__}.requests cannot be empty")
        self._client: httpx.AsyncClient | None = None

    async def setup(self) -> None:
        if not self.dry_run:
            self._client = create_client(self.base_url)

    async def teardown(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _next_spec(self, sequence: int) -> HttpRequestSpec:
        return self.requests[(sequence - 1) % len(self.requests)]

    async def issue_request(self, worker_id: int, sequence: int) -> WafObservation:
        spec = self._next_spec(sequence)
        if self.dry_run:
            return WafObservation(
                signal=WafSignal.NONE,
                status_code=None,
                location=None,
                elapsed_ms=0.0,
                endpoint=spec.path,
            )
        if self._client is None:
            raise RuntimeError("HttpBot.setup() not run (dry_run=False requires client)")

        start = time.monotonic()
        try:
            response = await self._client.request(
                spec.method,
                spec.path,
                json=spec.json_body,
                data=spec.data,
                headers=spec.headers,
            )
        except Exception as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            return observe_exception(exc, elapsed_ms, endpoint=spec.path)
        elapsed_ms = (time.monotonic() - start) * 1000
        return observe_response(response, elapsed_ms, endpoint=spec.path)
