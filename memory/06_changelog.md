# CHANGELOG

Formato: `[YYYY-MM-DD HH:MM:SS] Evento`.

---

## [2026-04-24]

- Kickoff sessione su progetto `bot-testing`.
- Analisi documento requisiti `Bot Testing Ad Arte_v1.2.docx`: obiettivo, 5 categorie BOT, stack tecnico, rischi, pianificazione.
- Analisi Excel `URL-WAF AntiBoT.xlsx` e `API_antiBot_AdArte.xlsx`: matrice endpoint target per categoria di protezione + endpoint Keycloak e ticketing.
- Lettura istruzioni operative (`C:\Users\Samuele\Downloads\istruzioni\`) files `00` - `11`.
- Decisione utente: esecuzione **locale** inizialmente, no VM Linode.
- Decisione utente: knowledge base **nel repository** (anziché `~/Desktop/memory/`) per consentire continuità cross-chat e collaborazione multi-persona.
- Decisione utente: repo GitHub privatizzato per contenere memory/ senza esporre dati operativi.
- Setup struttura `memory/` nel repo secondo schema `07_memory_and_operational_context.md` adattato:
  - `00_index.md` indice e regole
  - `01_infrastructure.md` endpoint, swagger, microservizi
  - `02_operations_access.md` come raggiungere l'ambiente, referenti, pattern secrets.md
  - `03_pipelines.md` repo, branching provvisorio, CI/CD out-of-scope
  - `04_dependencies.md` stack e dipendenze tra servizi
  - `05_quirks.md` prerequisiti bloccanti aperti e rischi noti
  - `06_changelog.md` questo file
  - `07_objectives.md` obiettivo tecnico, matrice BOT, out-of-scope
  - `08_endpoints.md` elenco completo endpoint target per categoria WAF
  - `secrets.md.example` template credenziali
- `.gitignore` creato per escludere `memory/secrets.md` e artefatti locali.
- Primo commit `0dc30aa bootstrap memory scaffolding` pushato su `origin/main` dopo privatizzazione.
- Decisione best practices (prompt utente "segui le best practices"):
  - Dep manager: `uv` (installato via `python -m pip install --user uv`, v0.11.7).
  - Runtime: Python 3.12 gestito da `uv` (no install system-wide).
  - Linter/formatter: `ruff` (sostituisce black+isort+flake8).
  - Type checker: `mypy` strict.
  - Layout: src-layout (`src/waf_bots/`).
  - Docker: `python:3.12-slim` + Playwright installato in build.
  - Branching: feature branch + PR su `main`, conventional commits.
  - Pre-commit hooks: ruff + mypy.
- Fix: accenti italiani reali in tutti i file memory (à, è, é, ì, ò, ù) rimpiazzando il workaround `a'`, `e'`, `u'`, ... come da regola `11_domain_documents.md`. Commit `b4c8305`.
- Branch `feature/scaffolding` creato da `main`.
- Scaffolding Python completato: `pyproject.toml` (PEP 621, Python 3.12, httpx + Playwright + dev tools), src-layout `src/waf_bots/` con `cli.py`, `common/` (logger JSON, client httpx async, browser Playwright, classifier segnali WAF, reporter), stub dei 5 BOT (`bots/dos.py`, `ato.py`, `registration.py`, `content_scraping.py`, `price_scraping.py`).
- Test: `test_cli.py`, `test_waf_signals.py`, `test_reporter.py` - 15/15 passed.
- Tooling: `.pre-commit-config.yaml`, `.python-version` (3.12), `.dockerignore`.
- Dockerfile: `python:3.12-slim` + uv + Playwright chromium con system deps, utente non-root `botrunner`, ENTRYPOINT `python -m waf_bots`.
- `README.md`: setup uv, uso CLI, struttura, prerequisiti bloccanti.
- Checks locali green: ruff format + ruff check OK, mypy strict OK (21 file), pytest 15/15, CLI `--help` e `--version` funzionanti.
- Fix ruff UP042: `WafSignal(str, Enum)` sostituito con `WafSignal(StrEnum)` (Python 3.11+).
- Commit `da09b08` su `feature/scaffolding`, pushato su origin.
- PR [#1](https://github.com/Aptul9/bot-testing/pull/1) aperta e mergiata via squash su `main` (commit `e34e129`). Branch `feature/scaffolding` eliminato da remote e local.
- Branch `feature/ci` creato da `main`.
- Pre-commit hooks installati localmente (`.git/hooks/pre-commit`).
- GitHub Actions workflow aggiunto (`.github/workflows/ci.yml`): job `checks` (ruff format, ruff lint, mypy strict, pytest) + job `docker` (build senza push, cache GHA). Trigger push/PR su `main`.
- Docker build locale `waf-bots:dev` lanciato in background per validazione Dockerfile.
- Dockerfile fix: `README.md` copiato prima di `uv run`, altrimenti la resolve metadata di hatchling fallisce.
- CI GitHub Actions prima esecuzione verde: job `checks` 16s, job `docker build` 2m25s.
- PR [#2](https://github.com/Aptul9/bot-testing/pull/2) mergiata via squash su `main` (commit `55f597c`). Branch `feature/ci` eliminato.

Prerequisiti bloccanti ancora aperti (vedi `05_quirks.md`): whitelist IP (SOC), credenziali test (Cliente), lista endpoint search BOT-1 (Cliente), conferma scope locale (Utente).
