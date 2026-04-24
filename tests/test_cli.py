"""Smoke test sul parser CLI."""

from __future__ import annotations

import pytest

from waf_bots.cli import BOT_NAMES, build_parser


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


def test_cli_parses_minimum() -> None:
    parser = build_parser()
    args = parser.parse_args(["--bot", "bot-1-dos"])
    assert args.bot == "bot-1-dos"
    assert args.duration == 60
    assert args.concurrency == 1


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
        ]
    )
    assert args.bot == "bot-2-ato"
    assert args.duration == 30
    assert args.concurrency == 4
    assert args.base_url == "https://example.invalid"
    assert args.output == "/tmp/out.json"


def test_bot_names_set() -> None:
    assert len(BOT_NAMES) == 5
    assert len(set(BOT_NAMES)) == 5
