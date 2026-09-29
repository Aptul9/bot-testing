"""BOT-2 Account Takeover. Target: il login che valida davvero le credenziali.

L'account takeover si esercita dove le password vengono verificate, cioè il
token endpoint di Keycloak (`POST /realms/{realm}/protocol/openid-connect/token`
con `grant_type=password`), non l'endpoint applicativo `/api/app/login`, che in
produzione accetta un JWT già valido e non fa alcuna verifica di password
(ritorna 500/403 se chiamato come una login utente/password).

Il BOT genera login ripetuti dallo stesso IP per triggerare la rilevazione ATO
del WAF. Un 401 è l'esito normale di un tentativo fallito e NON è un segnale di
blocco (vedi `classify`): il blocco si manifesta come 403/429/redirect di
challenge o reset di connessione.

Due modalità, scelte dalle env var:
- **Credential stuffing (default)**: nessuna credenziale reale, username fittizi
  distinti a ogni chiamata e password fissa errata. Nessun account reale viene
  bloccato (il lockout Keycloak è per-utente). È il default sicuro.
- **Brute force mirato**: se sono impostate `WAF_BOTS_ATO_USERNAME` e
  `WAF_BOTS_ATO_PASSWORD`, il BOT ripete i tentativi su quell'unico account.
  Può far scattare il lockout di quel solo account.

Env var:
- `WAF_BOTS_KEYCLOAK_BASE_URL`  default https://login.museiitaliani.it
- `WAF_BOTS_KEYCLOAK_REALM`     default AD-Arte-visitors
- `WAF_BOTS_ATO_CLIENT_ID`      default 77fb7823-... (client pubblico visitors)
- `WAF_BOTS_ATO_USERNAME` / `WAF_BOTS_ATO_PASSWORD`  opzionali (brute force mirato)
"""

from __future__ import annotations

import os
import time
import uuid
from typing import Any

import httpx

from waf_bots.bots.base import Bot
from waf_bots.common.http import (
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
    observe_exception,
    observe_response,
)
from waf_bots.common.waf_signals import WafObservation, WafSignal

KEYCLOAK_BASE_URL_ENV = "WAF_BOTS_KEYCLOAK_BASE_URL"
KEYCLOAK_REALM_ENV = "WAF_BOTS_KEYCLOAK_REALM"
ATO_CLIENT_ID_ENV = "WAF_BOTS_ATO_CLIENT_ID"
USERNAME_ENV = "WAF_BOTS_ATO_USERNAME"
PASSWORD_ENV = "WAF_BOTS_ATO_PASSWORD"

DEFAULT_KEYCLOAK_BASE_URL = "https://login.museiitaliani.it"
DEFAULT_REALM = "AD-Arte-visitors"
# Client pubblico "visitors" del realm (nessun secret, direct grant abilitato).
DEFAULT_CLIENT_ID = "77fb7823-2de9-47f3-a776-52191733e3cd"

# Password errata usata in modalità credential stuffing: fissa, palesemente non
# valida, così ogni tentativo è un login fallito (401).
STUFFING_PASSWORD = "WafAto!Invalid"


class AtoBot(Bot):
    """BOT-2 ATO: credential stuffing / brute force sul token endpoint Keycloak."""

    name = "bot-2-ato"

    def __init__(
        self,
        base_url: str,
        duration_s: int,
        concurrency: int = 1,
        *,
        dry_run: bool = True,
        rps_per_worker: float = 0.0,
    ) -> None:
        super().__init__(
            base_url,
            duration_s,
            concurrency,
            dry_run=dry_run,
            rps_per_worker=rps_per_worker,
        )
        self._kc_base = os.environ.get(KEYCLOAK_BASE_URL_ENV) or DEFAULT_KEYCLOAK_BASE_URL
        self._realm = os.environ.get(KEYCLOAK_REALM_ENV) or DEFAULT_REALM
        self._client_id = os.environ.get(ATO_CLIENT_ID_ENV) or DEFAULT_CLIENT_ID
        self._pinned_user = os.environ.get(USERNAME_ENV)
        self._pinned_pw = os.environ.get(PASSWORD_ENV)
        self._client: httpx.AsyncClient | None = None

    def _token_url(self) -> str:
        return f"/realms/{self._realm}/protocol/openid-connect/token"

    @property
    def _pinned(self) -> bool:
        """True quando si fa brute force mirato su un account reale."""
        return bool(self._pinned_user and self._pinned_pw)

    def _candidate(self, worker_id: int, sequence: int) -> tuple[str, str]:
        """Credenziali del prossimo tentativo.

        Mirato: sempre lo stesso account (da env). Stuffing: username distinto
        per chiamata più password fissa errata, così nessun account reale si
        blocca.
        """
        if self._pinned:
            return self._pinned_user, self._pinned_pw  # type: ignore[return-value]
        nonce = uuid.uuid4().hex[:8]
        username = f"waf-ato-{worker_id:02d}-{sequence:06d}-{nonce}@example.invalid"
        return username, STUFFING_PASSWORD

    async def setup(self) -> None:
        if self.dry_run:
            return
        self._client = httpx.AsyncClient(
            base_url=self._kc_base,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            timeout=DEFAULT_TIMEOUT,
            verify=True,
            http2=True,
            follow_redirects=False,
        )

    async def teardown(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def issue_request(self, worker_id: int, sequence: int) -> WafObservation:
        endpoint = self._token_url()
        if self.dry_run:
            return WafObservation(
                signal=WafSignal.NONE,
                status_code=None,
                location=None,
                elapsed_ms=0.0,
                endpoint=endpoint,
            )
        if self._client is None:
            raise RuntimeError("BOT-2 setup() not run (dry_run=False requires client)")

        username, password = self._candidate(worker_id, sequence)
        payload: dict[str, Any] = {
            "client_id": self._client_id,
            "grant_type": "password",
            "username": username,
            "password": password,
        }
        start = time.monotonic()
        try:
            response = await self._client.post(
                endpoint,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        except Exception as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            return observe_exception(exc, elapsed_ms, endpoint=endpoint)
        elapsed_ms = (time.monotonic() - start) * 1000
        return observe_response(response, elapsed_ms, endpoint=endpoint)
