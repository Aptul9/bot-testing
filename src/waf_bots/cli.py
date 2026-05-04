"""Entry point CLI per waf-bots."""

from __future__ import annotations

import argparse
import asyncio
import sys
from collections.abc import Mapping
from pathlib import Path

from waf_bots import __version__
from waf_bots.bots.ato import AtoBot
from waf_bots.bots.base import Bot
from waf_bots.bots.content_scraping import ContentScrapingBot
from waf_bots.bots.dos import DosBot
from waf_bots.bots.price_scraping import PriceScrapingBot
from waf_bots.bots.registration import RegistrationBot

DEFAULT_BASE_URL = "https://api-coll.museiitaliani.it"

_REGISTRY: Mapping[str, type[Bot]] = {
    "bot-1-dos": DosBot,
    "bot-2-ato": AtoBot,
    "bot-3-registration": RegistrationBot,
    "bot-4-content-scraping": ContentScrapingBot,
    "bot-5-price-scraping": PriceScrapingBot,
}

BOT_NAMES: list[str] = list(_REGISTRY)


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
        help=(
            "Worker count. HTTP BOTs share an async client; "
            "browser BOTs share a Playwright context (default: 1)"
        ),
    )
    parser.add_argument(
        "--rps",
        type=float,
        default=0.0,
        help=(
            "Per-worker requests-per-second cap (default: 0 = no cap). "
            "Aggregate target = rps * concurrency."
        ),
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Base URL API (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path del file JSON di output (default: stdout)",
    )
    safety = parser.add_mutually_exclusive_group()
    safety.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Modalita' simulata: nessuna richiesta inviata. DEFAULT.",
    )
    safety.add_argument(
        "--no-dry-run",
        dest="dry_run",
        action="store_false",
        help=(
            "Esecuzione reale contro il target. "
            "Per BOT-1 DoS richiede anche WAF_BOTS_ALLOW_DOS=true."
        ),
    )
    parser.set_defaults(dry_run=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    bot_cls = _REGISTRY[args.bot]
    bot = bot_cls(
        base_url=args.base_url,
        duration_s=args.duration,
        concurrency=args.concurrency,
        dry_run=args.dry_run,
        rps_per_worker=args.rps,
    )

    sys.stderr.write(
        f"[waf-bots] start {args.bot} duration={args.duration}s "
        f"concurrency={args.concurrency} rps={args.rps} dry_run={args.dry_run}\n"
    )
    try:
        report = asyncio.run(bot.run())
    except NotImplementedError as exc:
        sys.stderr.write(f"[waf-bots] BOT non ancora implementato: {exc}\n")
        return 2
    except RuntimeError as exc:
        sys.stderr.write(f"[waf-bots] safety check fallito: {exc}\n")
        return 3

    payload = report.to_json()
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
        sys.stderr.write(f"[waf-bots] report scritto in {args.output}\n")
    else:
        sys.stdout.write(payload + "\n")
    return 0
