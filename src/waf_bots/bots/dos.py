"""BOT-1 Denial of Service. Target: pagine di ricerca.

Implementazione prevista in fase successiva. Richiede la lista esatta degli
endpoint di search (prerequisito bloccante #3 in `memory/05_quirks.md`).
"""

from __future__ import annotations

from waf_bots.bots.base import Bot
from waf_bots.common.reporter import RunReport


class DosBot(Bot):
    name = "bot-1-dos"

    async def run(self) -> RunReport:
        raise NotImplementedError("BOT-1 non ancora implementato")
