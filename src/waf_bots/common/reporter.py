"""Serializzazione esito run BOT in JSON."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class RunReport:
    bot: str
    started_at: str
    ended_at: str
    duration_s: float
    requests_total: int
    first_block_after_s: float | None
    first_block_after_requests: int | None
    signals_count: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def new(bot: str) -> RunReport:
        now = datetime.now(tz=UTC).isoformat()
        return RunReport(
            bot=bot,
            started_at=now,
            ended_at=now,
            duration_s=0.0,
            requests_total=0,
            first_block_after_s=None,
            first_block_after_requests=None,
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    def write(self, path: Path) -> None:
        path.write_text(self.to_json(), encoding="utf-8")
