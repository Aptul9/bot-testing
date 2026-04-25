"""Serializzazione esito run BOT in JSON e aggregazione Markdown."""

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

    def to_markdown(self) -> str:
        lines = [f"### {self.bot}", ""]
        lines.append(f"- start: `{self.started_at}`")
        lines.append(f"- end:   `{self.ended_at}`")
        lines.append(f"- duration: {self.duration_s:.2f}s")
        lines.append(f"- richieste totali: {self.requests_total}")
        if self.first_block_after_s is not None:
            lines.append(
                f"- primo blocco dopo: {self.first_block_after_s:.2f}s "
                f"({self.first_block_after_requests} richieste)"
            )
        else:
            lines.append("- primo blocco: **mai osservato**")
        if self.metadata:
            meta = ", ".join(f"{k}={v}" for k, v in sorted(self.metadata.items()))
            lines.append(f"- metadata: {meta}")
        if self.signals_count:
            lines.append("")
            lines.append("| Segnale | Conteggio |")
            lines.append("|---|---|")
            for sig in sorted(self.signals_count):
                lines.append(f"| `{sig}` | {self.signals_count[sig]} |")
        lines.append("")
        return "\n".join(lines)


def consolidate(reports: list[RunReport], *, title: str = "Report run BOT") -> str:
    """Produce un report Markdown unico aggregando piu' RunReport."""
    if not reports:
        return f"# {title}\n\nNessun report fornito.\n"

    lines = [f"# {title}", ""]
    lines.append("## Sintesi")
    lines.append("")
    lines.append("| BOT | Richieste | Primo blocco (s) | Primo blocco (req) | Esito |")
    lines.append("|---|---|---|---|---|")
    for r in reports:
        first_s = f"{r.first_block_after_s:.2f}" if r.first_block_after_s is not None else "-"
        first_n = (
            str(r.first_block_after_requests) if r.first_block_after_requests is not None else "-"
        )
        outcome = "blocked" if r.first_block_after_s is not None else "non bloccato"
        lines.append(f"| `{r.bot}` | {r.requests_total} | {first_s} | {first_n} | {outcome} |")
    lines.append("")
    lines.append("## Dettaglio per BOT")
    lines.append("")
    for r in reports:
        lines.append(r.to_markdown())
    return "\n".join(lines)
