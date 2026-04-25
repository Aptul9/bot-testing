"""Test sul serializzatore RunReport e aggregazione Markdown."""

from __future__ import annotations

import json

from waf_bots.common.reporter import RunReport, consolidate


def test_runreport_new_roundtrip() -> None:
    report = RunReport.new("bot-1-dos")
    payload = json.loads(report.to_json())
    assert payload["bot"] == "bot-1-dos"
    assert payload["requests_total"] == 0
    assert payload["first_block_after_s"] is None
    assert payload["signals_count"] == {}


def test_runreport_to_markdown_includes_basic_fields() -> None:
    report = RunReport.new("bot-4-content-scraping")
    report.requests_total = 42
    report.duration_s = 12.34
    report.first_block_after_s = 3.21
    report.first_block_after_requests = 10
    report.signals_count = {"blocked_403": 5, "none": 37}
    report.metadata = {"base_url": "https://example.invalid"}

    md = report.to_markdown()
    assert "### bot-4-content-scraping" in md
    assert "richieste totali: 42" in md
    assert "primo blocco dopo: 3.21s (10 richieste)" in md
    assert "| `blocked_403` | 5 |" in md
    assert "base_url=https://example.invalid" in md


def test_runreport_to_markdown_no_block() -> None:
    report = RunReport.new("bot-5-price-scraping")
    report.requests_total = 100
    md = report.to_markdown()
    assert "primo blocco: **mai osservato**" in md


def test_consolidate_empty() -> None:
    md = consolidate([], title="Vuoto")
    assert "# Vuoto" in md
    assert "Nessun report fornito" in md


def test_consolidate_multi() -> None:
    a = RunReport.new("bot-1-dos")
    a.requests_total = 1000
    a.first_block_after_s = 5.5
    a.first_block_after_requests = 250
    a.signals_count = {"blocked_403": 750, "none": 250}

    b = RunReport.new("bot-4-content-scraping")
    b.requests_total = 200

    md = consolidate([a, b], title="Sintesi run")
    assert "# Sintesi run" in md
    assert "## Sintesi" in md
    assert "## Dettaglio per BOT" in md
    assert "| `bot-1-dos` | 1000 | 5.50 | 250 | blocked |" in md
    assert "| `bot-4-content-scraping` | 200 | - | - | non bloccato |" in md
    assert "### bot-1-dos" in md
    assert "### bot-4-content-scraping" in md
