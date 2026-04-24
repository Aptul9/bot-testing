"""Entry point CLI per waf-bots."""

from __future__ import annotations

import argparse
import sys

from waf_bots import __version__

BOT_NAMES: list[str] = [
    "bot-1-dos",
    "bot-2-ato",
    "bot-3-registration",
    "bot-4-content-scraping",
    "bot-5-price-scraping",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="waf-bots",
        description="BOT client per validazione antiBot WAF Fortinet su collaudo Ad Arte",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--bot",
        required=True,
        choices=BOT_NAMES,
        help="Nome del BOT da eseguire",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Durata della run in secondi (default: 60)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Concorrenza per i BOT HTTP async. Ignorato dai BOT browser (default: 1)",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Override del base URL API collaudo (default: da config)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path del file JSON di output (default: stdout)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    sys.stderr.write(f"[waf-bots] configurazione: {vars(args)}\n")
    sys.stderr.write("[waf-bots] implementazione dei BOT prevista nelle fasi successive.\n")
    return 0
