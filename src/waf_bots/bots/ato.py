"""BOT-2 Account Takeover. Target: login e reset password.

Il BOT genera login ripetuti su `POST /login` con credenziali di test (o,
in assenza, con valori dummy generati progressivamente). L'obiettivo non
e' autenticarsi ma triggerare la rilevazione ATO del WAF (pattern di login
falliti ripetuti dallo stesso IP).

Le credenziali reali, quando fornite dal cliente, vanno in env var:
- `WAF_BOTS_ATO_USERNAME`
- `WAF_BOTS_ATO_PASSWORD`

In assenza di queste, il BOT usa username sequenziali fittizi e password
casuale fissa. Il segnale WAF arriva comunque dal volume + frequenza.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import ClassVar

from waf_bots.bots.http_bot import HttpBot, HttpRequestSpec

API_PREFIX = "/smnadarte-integration-app-web/app/api"

USERNAME_ENV = "WAF_BOTS_ATO_USERNAME"
PASSWORD_ENV = "WAF_BOTS_ATO_PASSWORD"


def _credentials() -> tuple[str | None, str | None]:
    return os.environ.get(USERNAME_ENV), os.environ.get(PASSWORD_ENV)


class AtoBot(HttpBot):
    name = "bot-2-ato"

    requests: ClassVar[Sequence[HttpRequestSpec]] = (
        HttpRequestSpec(
            "POST",
            f"{API_PREFIX}/login",
            json_body={"username": "<placeholder>", "password": "<placeholder>"},
            headers={"Content-Type": "application/json"},
        ),
        HttpRequestSpec("GET", f"{API_PREFIX}/account/user"),
    )

    def _next_spec(self, sequence: int) -> HttpRequestSpec:
        spec = super()._next_spec(sequence)
        if spec.method != "POST" or spec.path != f"{API_PREFIX}/login":
            return spec
        username_env, password_env = _credentials()
        username = username_env or f"waf-test-{sequence:06d}@example.invalid"
        password = password_env or "WafTest!Invalid"
        # Ricreare lo spec per non mutare l'oggetto condiviso tra worker.
        return HttpRequestSpec(
            "POST",
            spec.path,
            json_body={"username": username, "password": password},
            headers=spec.headers,
        )
