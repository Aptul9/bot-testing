"""Tests for BOT-3 RegistrationBot (HTTP admin flow)."""

from __future__ import annotations

import pytest

from waf_bots.bots.registration import (
    DEFAULT_ADMIN_CLIENT_ID,
    DEFAULT_KEYCLOAK_BASE_URL,
    DEFAULT_REALM,
    KEYCLOAK_ADMIN_CLIENT_ID_ENV,
    KEYCLOAK_ADMIN_PASSWORD_ENV,
    KEYCLOAK_ADMIN_USER_ENV,
    KEYCLOAK_BASE_URL_ENV,
    KEYCLOAK_REALM_ENV,
    RegistrationBot,
)


def _bot(monkeypatch: pytest.MonkeyPatch, **env: str) -> RegistrationBot:
    for k in (
        KEYCLOAK_BASE_URL_ENV,
        KEYCLOAK_REALM_ENV,
        KEYCLOAK_ADMIN_CLIENT_ID_ENV,
        KEYCLOAK_ADMIN_USER_ENV,
        KEYCLOAK_ADMIN_PASSWORD_ENV,
    ):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    return RegistrationBot(base_url="https://api-coll.museiitaliani.it", duration_s=1)


def test_default_endpoints(monkeypatch: pytest.MonkeyPatch) -> None:
    bot = _bot(monkeypatch)
    assert bot._kc_base == DEFAULT_KEYCLOAK_BASE_URL
    assert bot._realm == DEFAULT_REALM
    assert bot._client_id == DEFAULT_ADMIN_CLIENT_ID
    assert bot._token_url() == f"/realms/{DEFAULT_REALM}/protocol/openid-connect/token"
    assert bot._users_url() == f"/admin/realms/{DEFAULT_REALM}/users"


def test_env_overrides_endpoints(monkeypatch: pytest.MonkeyPatch) -> None:
    bot = _bot(
        monkeypatch,
        WAF_BOTS_KEYCLOAK_BASE_URL="https://kc.example.invalid",
        WAF_BOTS_KEYCLOAK_REALM="custom-realm",
        WAF_BOTS_KEYCLOAK_ADMIN_CLIENT_ID="custom-cli",
    )
    assert bot._kc_base == "https://kc.example.invalid"
    assert bot._realm == "custom-realm"
    assert bot._client_id == "custom-cli"


def test_user_payload_unique_per_call(monkeypatch: pytest.MonkeyPatch) -> None:
    bot = _bot(monkeypatch)
    a = bot._build_user_payload(0, 1)
    b = bot._build_user_payload(0, 1)
    assert a["username"] != b["username"]
    assert a["email"].endswith("@example.invalid")
    assert a["credentials"][0]["type"] == "password"
    assert a["credentials"][0]["temporary"] is False


@pytest.mark.asyncio
async def test_dry_run_returns_none_observation(monkeypatch: pytest.MonkeyPatch) -> None:
    bot = _bot(monkeypatch)
    report = await bot.run()
    assert report.metadata["dry_run"] is True
    assert report.requests_total >= 1
    assert report.signals_count.get("none", 0) == report.requests_total
    # All observations must carry the admin endpoint, not the API base
    expected_endpoint = f"/admin/realms/{DEFAULT_REALM}/users"
    for ep_key in report.signals_by_endpoint:
        assert ep_key == expected_endpoint


@pytest.mark.asyncio
async def test_real_run_requires_admin_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bot = RegistrationBot(
        base_url="https://api-coll.museiitaliani.it",
        duration_s=1,
        dry_run=False,
    )
    monkeypatch.delenv(KEYCLOAK_ADMIN_USER_ENV, raising=False)
    monkeypatch.delenv(KEYCLOAK_ADMIN_PASSWORD_ENV, raising=False)
    bot._admin_user = None
    bot._admin_pw = None
    with pytest.raises(RuntimeError, match="WAF_BOTS_KEYCLOAK_ADMIN"):
        await bot.run()
