"""BOT-3 Creazione automatizzata di account. Target: registrazione/iscrizione."""

from __future__ import annotations

from waf_bots.bots.base import Bot
from waf_bots.common.waf_signals import WafObservation


class RegistrationBot(Bot):
    name = "bot-3-registration"

    async def issue_request(self, worker_id: int, sequence: int) -> WafObservation:
        raise NotImplementedError("BOT-3 non ancora implementato")
