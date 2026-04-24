"""Classe base per i BOT."""

from __future__ import annotations

from abc import ABC, abstractmethod

from waf_bots.common.reporter import RunReport


class Bot(ABC):
    name: str

    def __init__(self, base_url: str, duration_s: int, concurrency: int = 1) -> None:
        self.base_url = base_url
        self.duration_s = duration_s
        self.concurrency = concurrency

    @abstractmethod
    async def run(self) -> RunReport: ...
