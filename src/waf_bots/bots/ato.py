"""BOT-2 Account Takeover. Target: login e reset password."""

from __future__ import annotations

from waf_bots.bots.base import Bot
from waf_bots.common.waf_signals import WafObservation


class AtoBot(Bot):
    name = "bot-2-ato"

    async def issue_request(self, worker_id: int, sequence: int) -> WafObservation:
        raise NotImplementedError("BOT-2 non ancora implementato")
