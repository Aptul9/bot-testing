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
- Fix: accenti italiani reali in tutti i file memory (à, è, é, ì, ò, ù) rimpiazzando il workaround `a'`, `e'`, `u'`, ... come da regola `11_domain_documents.md`.

Prerequisiti bloccanti ancora aperti (vedi `05_quirks.md`): whitelist IP (SOC), credenziali test (Cliente), lista endpoint search BOT-1 (Cliente), conferma scope locale (Utente).
