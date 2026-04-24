"""BOT-2 Account Takeover. Target: login e reset password."""

from __future__ import annotations

from waf_bots.bots.base import Bot
from waf_bots.common.reporter import RunReport


class AtoBot(Bot):
    name = "bot-2-ato"

    async def run(self) -> RunReport:
        raise NotImplementedError("BOT-2 non ancora implementato")
