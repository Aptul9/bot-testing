"""JSON serialization of BOT run results + Markdown aggregation."""

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
    signals_by_endpoint: dict[str, dict[str, int]] = field(default_factory=dict)
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
        lines.append(f"- requests total: {self.requests_total}")
        if self.first_block_after_s is not None:
            lines.append(
                f"- first block after: {self.first_block_after_s:.2f}s "
                f"({self.first_block_after_requests} requests)"
            )
        else:
            lines.append("- first block: **never observed**")
        if self.metadata:
            meta = ", ".join(f"{k}={v}" for k, v in sorted(self.metadata.items()))
            lines.append(f"- metadata: {meta}")
        if self.signals_count:
            lines.append("")
            lines.append("**Signals (aggregate)**")
            lines.append("")
            lines.append("| Signal | Count |")
            lines.append("|---|---|")
            for sig in sorted(self.signals_count):
                lines.append(f"| `{sig}` | {self.signals_count[sig]} |")
        if self.signals_by_endpoint:
            lines.append("")
            lines.append("**Signals per endpoint**")
            lines.append("")
            all_signals = sorted({s for sub in self.signals_by_endpoint.values() for s in sub})
            header = "| Endpoint | " + " | ".join(f"`{s}`" for s in all_signals) + " |"
            sep = "|---|" + "|".join(["---"] * len(all_signals)) + "|"
            lines.append(header)
            lines.append(sep)
            for ep in sorted(self.signals_by_endpoint):
                row = self.signals_by_endpoint[ep]
                cells = " | ".join(str(row.get(s, 0)) for s in all_signals)
                lines.append(f"| `{ep}` | {cells} |")
        lines.append("")
        return "\n".join(lines)


def consolidate(reports: list[RunReport], *, title: str = "BOT run report") -> str:
    """Build a single Markdown report aggregating multiple RunReport objects."""
    if not reports:
        return f"# {title}\n\nNo reports provided.\n"

    lines = [f"# {title}", ""]
    lines.append("## Summary")
    lines.append("")
    lines.append("| BOT | Requests | First block (s) | First block (req) | Outcome |")
    lines.append("|---|---|---|---|---|")
    for r in reports:
        first_s = f"{r.first_block_after_s:.2f}" if r.first_block_after_s is not None else "-"
        first_n = (
            str(r.first_block_after_requests) if r.first_block_after_requests is not None else "-"
        )
        outcome = "blocked" if r.first_block_after_s is not None else "not blocked"
        lines.append(f"| `{r.bot}` | {r.requests_total} | {first_s} | {first_n} | {outcome} |")
    lines.append("")
    lines.append("## Per-BOT detail")
    lines.append("")
    for r in reports:
        lines.append(r.to_markdown())
    return "\n".join(lines)
