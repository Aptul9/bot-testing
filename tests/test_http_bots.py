"""Test sui BOT HTTP-only (BOT-1 DoS, BOT-2 ATO) in modalita' dry-run."""

from __future__ import annotations

import pytest

from waf_bots.bots.ato import API_PREFIX as ATO_API_PREFIX
from waf_bots.bots.ato import AtoBot
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


def test_ato_bot_targets_login_and_account() -> None:
    paths = [r.path for r in AtoBot.requests]
    assert f"{ATO_API_PREFIX}/login" in paths
    assert f"{ATO_API_PREFIX}/account/user" in paths


def test_ato_bot_rotates_username_per_sequence() -> None:
    bot = AtoBot(base_url="https://x.invalid", duration_s=1)
    s1 = bot._next_spec(1)
    s3 = bot._next_spec(3)
    assert s1.path == f"{ATO_API_PREFIX}/login"
    assert s3.path == f"{ATO_API_PREFIX}/login"  # ciclo torna a login (2 specs, dispari)
    assert isinstance(s1.json_body, dict)
    assert isinstance(s3.json_body, dict)
    assert s1.json_body["username"] != s3.json_body["username"]


def test_ato_bot_uses_env_credentials_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WAF_BOTS_ATO_USERNAME", "real@example.com")
    monkeypatch.setenv("WAF_BOTS_ATO_PASSWORD", "secret")
    bot = AtoBot(base_url="https://x.invalid", duration_s=1)
    spec = bot._next_spec(1)
    assert isinstance(spec.json_body, dict)
    assert spec.json_body == {"username": "real@example.com", "password": "secret"}


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
