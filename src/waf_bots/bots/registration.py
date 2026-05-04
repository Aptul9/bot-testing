"""BOT-3 Automated account creation. Target: Keycloak admin user creation API.

The bot uses the realm admin (or a service account) to POST new visitor users
on `/admin/realms/{realm}/users`. This is the most reliable path because the
admin endpoint is stable and well documented; if Almaviva exposes a public
self-registration endpoint in the future, a sibling BrowserBot can be added.

Env vars consumed:
  WAF_BOTS_KEYCLOAK_BASE_URL     default https://login-coll.museiitaliani.it
  WAF_BOTS_KEYCLOAK_REALM        default AD-Arte-visitors
  WAF_BOTS_KEYCLOAK_ADMIN_CLIENT_ID  default admin-cli
  WAF_BOTS_KEYCLOAK_ADMIN_USER   required for --no-dry-run
  WAF_BOTS_KEYCLOAK_ADMIN_PASSWORD  required for --no-dry-run

Real flow per issue_request:
  1. If no cached admin token (or expired): POST realm token endpoint with
     password grant, cache the access_token + refresh deadline
  2. POST /admin/realms/{realm}/users with a unique username + random password
  3. Map response -> WafObservation. 201/204 = NONE, 4xx = blocked signal
     per status code, exception -> observe_exception
"""

from __future__ import annotations

import asyncio
import os
import secrets
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
from waf_bots.common.logger import get_logger
from waf_bots.common.waf_signals import WafObservation, WafSignal

KEYCLOAK_BASE_URL_ENV = "WAF_BOTS_KEYCLOAK_BASE_URL"
KEYCLOAK_REALM_ENV = "WAF_BOTS_KEYCLOAK_REALM"
KEYCLOAK_ADMIN_CLIENT_ID_ENV = "WAF_BOTS_KEYCLOAK_ADMIN_CLIENT_ID"
KEYCLOAK_ADMIN_USER_ENV = "WAF_BOTS_KEYCLOAK_ADMIN_USER"
KEYCLOAK_ADMIN_PASSWORD_ENV = "WAF_BOTS_KEYCLOAK_ADMIN_PASSWORD"

DEFAULT_KEYCLOAK_BASE_URL = "https://login-coll.museiitaliani.it"
DEFAULT_REALM = "AD-Arte-visitors"
DEFAULT_ADMIN_CLIENT_ID = "admin-cli"

TOKEN_REFRESH_MARGIN_S = 5.0


class RegistrationBot(Bot):
    name = "bot-3-registration"

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
        self._client_id = os.environ.get(KEYCLOAK_ADMIN_CLIENT_ID_ENV) or DEFAULT_ADMIN_CLIENT_ID
        self._admin_user = os.environ.get(KEYCLOAK_ADMIN_USER_ENV)
        self._admin_pw = os.environ.get(KEYCLOAK_ADMIN_PASSWORD_ENV)
        self._client: httpx.AsyncClient | None = None
        self._token: str | None = None
        self._token_exp: float = 0.0
        self._token_lock = asyncio.Lock()
        self._kc_log = get_logger(f"waf_bots.{self.name}.keycloak")

    def _token_url(self) -> str:
        return f"/realms/{self._realm}/protocol/openid-connect/token"

    def _users_url(self) -> str:
        return f"/admin/realms/{self._realm}/users"

    async def setup(self) -> None:
        if self.dry_run:
            return
        if not (self._admin_user and self._admin_pw):
            raise RuntimeError(
                f"BOT-3 real run requires {KEYCLOAK_ADMIN_USER_ENV} and "
                f"{KEYCLOAK_ADMIN_PASSWORD_ENV} env vars. Populate from "
                f"[[_secrets/antibot]] before running."
            )
        self._client = httpx.AsyncClient(
            base_url=self._kc_base,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            timeout=DEFAULT_TIMEOUT,
            verify=True,
            http2=True,
            follow_redirects=False,
        )
        await self._refresh_token()

    async def teardown(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _refresh_token(self) -> None:
        if self._client is None:
            raise RuntimeError("client not initialized")
        if not (self._admin_user and self._admin_pw):
            raise RuntimeError("admin credentials not set")
        resp = await self._client.post(
            self._token_url(),
            data={
                "client_id": self._client_id,
                "username": self._admin_user,
                "password": self._admin_pw,
                "grant_type": "password",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        self._token = data["access_token"]
        # Keycloak default access token lifespan ~60s; refresh slightly early.
        self._token_exp = time.monotonic() + float(data.get("expires_in", 60))

    async def _ensure_token(self) -> None:
        # Lock prevents concurrent refresh requests when many workers
        # simultaneously observe an expired token.
        async with self._token_lock:
            if not self._token or time.monotonic() >= self._token_exp - TOKEN_REFRESH_MARGIN_S:
                await self._refresh_token()

    @staticmethod
    def _build_user_payload(worker_id: int, sequence: int) -> dict[str, Any]:
        # Unique-per-call username + email so admin POST never collides.
        nonce = uuid.uuid4().hex[:8]
        username = f"waf-test-{worker_id:02d}-{sequence:06d}-{nonce}"
        return {
            "username": username,
            "email": f"{username}@example.invalid",
            "enabled": True,
            "emailVerified": False,
            "firstName": "WAF",
            "lastName": "Test",
            "credentials": [
                {
                    "type": "password",
                    "value": secrets.token_urlsafe(16),
                    "temporary": False,
                }
            ],
        }

    async def issue_request(self, worker_id: int, sequence: int) -> WafObservation:
        endpoint = self._users_url()
        if self.dry_run:
            return WafObservation(
                signal=WafSignal.NONE,
                status_code=None,
                location=None,
                elapsed_ms=0.0,
                endpoint=endpoint,
            )
        if self._client is None:
            raise RuntimeError("BOT-3 setup() not run")

        try:
            await self._ensure_token()
        except Exception as exc:
            return observe_exception(exc, 0.0, endpoint=self._token_url())

        payload = self._build_user_payload(worker_id, sequence)
        start = time.monotonic()
        try:
            response = await self._client.post(
                endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {self._token}"},
            )
        except Exception as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            return observe_exception(exc, elapsed_ms, endpoint=endpoint)
        elapsed_ms = (time.monotonic() - start) * 1000

        # Refresh token on 401, then count this attempt as the response we got.
        if response.status_code == 401:
            try:
                async with self._token_lock:
                    await self._refresh_token()
            except Exception as exc:
                self._kc_log.warning(
                    "token_refresh_failed_on_401",
                    extra={"extra_fields": {"error": repr(exc)}},
                )

        return observe_response(response, elapsed_ms, endpoint=endpoint)
