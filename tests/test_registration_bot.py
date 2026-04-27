"""Smoke tests for BOT-3 RegistrationBot (no Playwright launch)."""

from __future__ import annotations

import pytest

from waf_bots.bots.registration import KEYCLOAK_BASE_URL_ENV, RegistrationBot


def test_registration_paths_target_keycloak_realm() -> None:
    assert len(RegistrationBot.paths) >= 2
    for p in RegistrationBot.paths:
        assert "/realms/AD-Arte-visitors" in p


def test_registration_default_base_url_falls_back_to_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(KEYCLOAK_BASE_URL_ENV, raising=False)
    bot = RegistrationBot(base_url="https://api-coll.museiitaliani.it", duration_s=1)
    url = bot._next_url(1)
    assert url.startswith("https://api-coll.museiitaliani.it/")
    assert "/realms/AD-Arte-visitors" in url


def test_registration_uses_env_keycloak_base(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(KEYCLOAK_BASE_URL_ENV, "https://keycloak-coll.museiitaliani.it")
    bot = RegistrationBot(base_url="https://api-coll.museiitaliani.it", duration_s=1)
    url = bot._next_url(1)
    assert url.startswith("https://keycloak-coll.museiitaliani.it/")
    assert "/realms/AD-Arte-visitors/protocol/openid-connect/registrations" in url


def test_registration_cycles_through_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(KEYCLOAK_BASE_URL_ENV, "https://keycloak.invalid")
    bot = RegistrationBot(base_url="https://x.invalid", duration_s=1)
    n = len(RegistrationBot.paths)
    urls = {bot._next_url(i) for i in range(1, n + 1)}
    assert len(urls) == n
