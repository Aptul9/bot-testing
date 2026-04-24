"""Test sul serializzatore RunReport."""

from __future__ import annotations

import json

from waf_bots.common.reporter import RunReport


def test_runreport_new_roundtrip() -> None:
    report = RunReport.new("bot-1-dos")
    payload = json.loads(report.to_json())
    assert payload["bot"] == "bot-1-dos"
    assert payload["requests_total"] == 0
    assert payload["first_block_after_s"] is None
    assert payload["signals_count"] == {}
