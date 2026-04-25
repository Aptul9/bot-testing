"""BOT-1 Denial of Service. Target: pagine di ricerca (cms-ms cached).

Endpoint candidati identificati da swagger pubblico cms-ms. La lista esatta
va confermata dal cliente: vedere `## Cose da chiedere agli stakeholder` -
`## Al cliente Ad Arte - lista endpoint pagine di ricerca` nella nota di
progetto antibot del vault.

SAFETY: anche con `--no-dry-run`, BOT-1 richiede env var
`WAF_BOTS_ALLOW_DOS=true` per partire. Senza di essa, il run fallisce in
setup. Questo previene esecuzioni accidentali contro il backend di
collaudo. Pre-mortem documentato richiesto prima di ogni run reale (vedi
`08_advanced_safety_time_and_pipelines.md` sez. 2).
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import ClassVar

from waf_bots.bots.http_bot import HttpBot, HttpRequestSpec

CMS_MS_PREFIX = "/cms-ms/api/public/cached"
ALLOW_DOS_ENV = "WAF_BOTS_ALLOW_DOS"
SAMPLE_MUSEUM_ID = "1"


class DosBot(HttpBot):
    name = "bot-1-dos"

    requests: ClassVar[Sequence[HttpRequestSpec]] = (
        HttpRequestSpec("GET", f"{CMS_MS_PREFIX}/museum/"),
        HttpRequestSpec("GET", f"{CMS_MS_PREFIX}/museum-with-e-ticketing"),
        HttpRequestSpec("GET", f"{CMS_MS_PREFIX}/museum/{SAMPLE_MUSEUM_ID}"),
        HttpRequestSpec("GET", f"{CMS_MS_PREFIX}/overview"),
    )

    async def setup(self) -> None:
        if not self.dry_run and os.environ.get(ALLOW_DOS_ENV, "").lower() != "true":
            raise RuntimeError(
                f"BOT-1 DoS in modalita' reale richiede env var "
                f"{ALLOW_DOS_ENV}=true. Impostarla solo dopo aver verificato "
                f"i prerequisiti (whitelist WAF, conferma scope) e dopo aver "
                f"documentato il pre-mortem."
            )
        await super().setup()
