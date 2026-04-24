# PIPELINES AND CI/CD

## Stato attuale

**CI attiva** su GitHub Actions (`.github/workflows/ci.yml`) solo per validazione:

- Trigger: push su `main`, pull request verso `main`.
- Job `checks` (Ubuntu): `uv sync --frozen`, `ruff format --check`, `ruff check`, `mypy` strict, `pytest`.
- Job `docker` (dipende da checks): build immagine Docker senza push, con cache GHA.
- Concurrency group per branch con `cancel-in-progress`.

**CD deliberatamente fuori scope** (vedi `07_objectives.md`): nessun deploy automatico, nessun push su registry. La costruzione dell'immagine di release resta manuale (`docker build` locale).

## Repository

| Campo | Valore |
|---|---|
| URL | `https://github.com/Aptul9/bot-testing` |
| Default branch | `main` |
| Visibilità | Privato (cambio richiesto il 2026-04-24 prima del primo push) |
| Owner git user locale | `Aptul` |

## Branching strategy

Decisione 2026-04-24: **feature branch + PR su `main`**, conventional commits.

- `main` contiene solo storia mergeata tramite PR.
- Ogni fase operativa (scaffolding, BOT-1, BOT-2, ...) su feature branch dedicato, es. `feature/scaffolding`, `feature/bot-1-dos`.
- Merge via squash o rebase, a discrezione dell'owner.
- Commit message: conventional commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`).

Unica eccezione storica: il commit iniziale `bootstrap memory scaffolding` è stato fatto direttamente su `main` quando il repo era vuoto e non c'era ancora una storia da proteggere.

Strumenti:
- `gh` CLI per apertura PR (richiede `gh auth login` sulla macchina dell'operatore).
- Pre-commit hook (`ruff`, `mypy`) configurati in `.pre-commit-config.yaml`.

## Build artifact

- Singola immagine Docker `waf-bots` contenente tutti i BOT (HTTP + browser).
- Base image: `python:3.12-slim` + Playwright installato in build.
- Build eseguita localmente. Nessun registry esterno previsto per questa iniziativa.
- Tag immagine: semver (`v0.1.0`, `v0.2.0`, ...) agganciato al tag git.
