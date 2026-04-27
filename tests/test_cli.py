"""Smoke test sul parser CLI e dispatch dei BOT."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from waf_bots.cli import BOT_NAMES, build_parser, main


def test_cli_help_exits_zero() -> None:
    parser = build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--help"])
    assert exc.value.code == 0


def test_cli_requires_bot() -> None:
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_cli_rejects_unknown_bot() -> None:
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--bot", "bot-99-unknown"])


def test_cli_parses_minimum_with_default_dry_run() -> None:
    parser = build_parser()
    args = parser.parse_args(["--bot", "bot-1-dos"])
    assert args.bot == "bot-1-dos"
    assert args.duration == 60
    assert args.concurrency == 1
    assert args.rps == 0.0
    assert args.dry_run is True


def test_cli_rps_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--bot", "bot-1-dos", "--rps", "2.5"])
    assert args.rps == 2.5


def test_cli_dry_run_flag_can_be_disabled() -> None:
    parser = build_parser()
    args = parser.parse_args(["--bot", "bot-1-dos", "--no-dry-run"])
    assert args.dry_run is False


def test_cli_full_args() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "--bot",
            "bot-2-ato",
            "--duration",
            "30",
            "--concurrency",
            "4",
            "--base-url",
            "https://example.invalid",
            "--output",
            "/tmp/out.json",
            "--no-dry-run",
        ]
    )
    assert args.bot == "bot-2-ato"
    assert args.duration == 30
    assert args.concurrency == 4
    assert args.base_url == "https://example.invalid"
    assert args.output == "/tmp/out.json"
    assert args.dry_run is False


def test_bot_names_set() -> None:
    assert len(BOT_NAMES) == 5
    assert len(set(BOT_NAMES)) == 5


def test_main_dry_run_dos_writes_json_to_stdout(
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main(["--bot", "bot-1-dos", "--duration", "1"])
    assert rc == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["bot"] == "bot-1-dos"
    assert payload["metadata"]["dry_run"] is True


def test_main_dry_run_writes_to_output_file(tmp_path: Path) -> None:
    out = tmp_path / "report.json"
    rc = main(["--bot", "bot-5-price-scraping", "--duration", "1", "--output", str(out)])
    assert rc == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["bot"] == "bot-5-price-scraping"


def test_main_dry_run_bot3_returns_zero(tmp_path: Path) -> None:
    # BOT-3 is now a BrowserBot subclass; dry-run no longer raises.
    out = tmp_path / "report.json"
    rc = main(["--bot", "bot-3-registration", "--duration", "1", "--output", str(out)])
    assert rc == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["bot"] == "bot-3-registration"
    assert payload["metadata"]["dry_run"] is True
