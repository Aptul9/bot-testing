"""Test sui BOT HTTP-only (BOT-1 DoS, BOT-2 ATO) in modalita' dry-run."""

from __future__ import annotations

import pytest

from waf_bots.bots.ato import (
    ATO_CLIENT_ID_ENV,
    DEFAULT_CLIENT_ID,
    DEFAULT_KEYCLOAK_BASE_URL,
    DEFAULT_REALM,
    KEYCLOAK_BASE_URL_ENV,
    KEYCLOAK_REALM_ENV,
    PASSWORD_ENV,
    STUFFING_PASSWORD,
    USERNAME_ENV,
    AtoBot,
)
from waf_bots.bots.dos import ALLOW_DOS_ENV, CMS_MS_PREFIX, DosBot
from waf_bots.bots.http_bot import HttpBot, HttpRequestSpec
from waf_bots.common.waf_signals import WafSignal


def test_http_bot_rejects_empty_requests() -> None:
    class EmptyBot(HttpBot):
        name = "empty"

    with pytest.raises(ValueError, match="requests"):
        EmptyBot(base_url="https://x.invalid", duration_s=1)


def test_dos_bot_paths_under_cms_ms_cached() -> None:
    assert len(DosBot.requests) >= 4
    for spec in DosBot.requests:
        assert spec.method == "GET"
        assert spec.path.startswith(CMS_MS_PREFIX)


def _clean_ato_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for k in (
        KEYCLOAK_BASE_URL_ENV,
        KEYCLOAK_REALM_ENV,
        ATO_CLIENT_ID_ENV,
        USERNAME_ENV,
        PASSWORD_ENV,
    ):
        monkeypatch.delenv(k, raising=False)


def test_ato_bot_targets_keycloak_token_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    _clean_ato_env(monkeypatch)
    bot = AtoBot(base_url="https://x.invalid", duration_s=1)
    assert bot._kc_base == DEFAULT_KEYCLOAK_BASE_URL
    assert bot._realm == DEFAULT_REALM
    assert bot._client_id == DEFAULT_CLIENT_ID
    assert bot._token_url() == f"/realms/{DEFAULT_REALM}/protocol/openid-connect/token"


def test_ato_bot_env_overrides_target(monkeypatch: pytest.MonkeyPatch) -> None:
    _clean_ato_env(monkeypatch)
    monkeypatch.setenv(KEYCLOAK_BASE_URL_ENV, "https://kc.example.invalid")
    monkeypatch.setenv(KEYCLOAK_REALM_ENV, "custom-realm")
    monkeypatch.setenv(ATO_CLIENT_ID_ENV, "custom-client")
    bot = AtoBot(base_url="https://x.invalid", duration_s=1)
    assert bot._kc_base == "https://kc.example.invalid"
    assert bot._realm == "custom-realm"
    assert bot._client_id == "custom-client"
    assert bot._token_url() == "/realms/custom-realm/protocol/openid-connect/token"


def test_ato_bot_stuffing_rotates_username_per_call(monkeypatch: pytest.MonkeyPatch) -> None:
    _clean_ato_env(monkeypatch)
    bot = AtoBot(base_url="https://x.invalid", duration_s=1)
    assert bot._pinned is False
    u1, p1 = bot._candidate(0, 1)
    u2, p2 = bot._candidate(0, 1)
    assert u1 != u2  # username distinto per chiamata: nessun account reale si blocca
    assert u1.endswith("@example.invalid")
    assert p1 == p2 == STUFFING_PASSWORD


def test_ato_bot_pinned_credentials_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    _clean_ato_env(monkeypatch)
    monkeypatch.setenv(USERNAME_ENV, "real@example.com")
    monkeypatch.setenv(PASSWORD_ENV, "secret")
    bot = AtoBot(base_url="https://x.invalid", duration_s=1)
    assert bot._pinned is True
    assert bot._candidate(0, 1) == ("real@example.com", "secret")
    assert bot._candidate(3, 9) == ("real@example.com", "secret")  # sempre lo stesso account


@pytest.mark.asyncio
async def test_dos_bot_dry_run_does_not_open_client() -> None:
    bot = DosBot(base_url="https://api-coll.museiitaliani.it", duration_s=1, dry_run=True)
    report = await bot.run()
    assert report.metadata["dry_run"] is True
    assert report.requests_total >= 1
    # In dry-run tutto e' classificato NONE, nessun blocco osservato.
    assert report.first_block_after_s is None
    assert report.signals_count.get(WafSignal.NONE.value, 0) == report.requests_total


@pytest.mark.asyncio
async def test_dos_bot_real_run_requires_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ALLOW_DOS_ENV, raising=False)
    bot = DosBot(base_url="https://x.invalid", duration_s=1, dry_run=False)
    with pytest.raises(RuntimeError, match=ALLOW_DOS_ENV):
        await bot.run()


def test_request_spec_normalizes_method() -> None:
    spec = HttpRequestSpec("get", "/x")
    assert spec.method == "GET"
