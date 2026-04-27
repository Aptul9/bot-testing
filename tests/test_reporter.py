"""Tests on RunReport serializer and Markdown aggregation."""

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
    assert payload["signals_by_endpoint"] == {}


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
    assert "requests total: 42" in md
    assert "first block after: 3.21s (10 requests)" in md
    assert "| `blocked_403` | 5 |" in md
    assert "base_url=https://example.invalid" in md


def test_runreport_to_markdown_no_block() -> None:
    report = RunReport.new("bot-5-price-scraping")
    report.requests_total = 100
    md = report.to_markdown()
    assert "first block: **never observed**" in md


def test_runreport_to_markdown_with_per_endpoint_breakdown() -> None:
    report = RunReport.new("bot-1-dos")
    report.requests_total = 3
    report.signals_by_endpoint = {
        "/cms-ms/api/public/cached/museum/": {"blocked_403": 2, "none": 1},
        "/cms-ms/api/public/cached/overview": {"none": 1},
    }
    md = report.to_markdown()
    assert "Signals per endpoint" in md
    assert "/cms-ms/api/public/cached/museum/" in md
    assert "`blocked_403`" in md
    assert "`none`" in md


def test_consolidate_empty() -> None:
    md = consolidate([], title="Empty")
    assert "# Empty" in md
    assert "No reports provided" in md


def test_consolidate_multi() -> None:
    a = RunReport.new("bot-1-dos")
    a.requests_total = 1000
    a.first_block_after_s = 5.5
    a.first_block_after_requests = 250
    a.signals_count = {"blocked_403": 750, "none": 250}

    b = RunReport.new("bot-4-content-scraping")
    b.requests_total = 200

    md = consolidate([a, b], title="Run summary")
    assert "# Run summary" in md
    assert "## Summary" in md
    assert "## Per-BOT detail" in md
    assert "| `bot-1-dos` | 1000 | 5.50 | 250 | blocked |" in md
    assert "| `bot-4-content-scraping` | 200 | - | - | not blocked |" in md
    assert "### bot-1-dos" in md
    assert "### bot-4-content-scraping" in md
