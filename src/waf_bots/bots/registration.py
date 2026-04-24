"""BOT-3 Creazione automatizzata di account. Target: registrazione/iscrizione."""

from __future__ import annotations

from waf_bots.bots.base import Bot
from waf_bots.common.reporter import RunReport


class RegistrationBot(Bot):
    name = "bot-3-registration"

    async def run(self) -> RunReport:
        raise NotImplementedError("BOT-3 non ancora implementato")
