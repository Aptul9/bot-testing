# waf-bots

BOT client per la validazione delle protezioni antiBot del WAF Fortinet FortiGate sull'ambiente di collaudo Ad Arte.

Contesto, obiettivi, matrice BOT, endpoint target, rischi e prerequisiti sono documentati in `memory/` (lettura consigliata in ordine: `07_objectives.md`, `01_infrastructure.md`, `08_endpoints.md`, `05_quirks.md`).

## Requisiti

- Python 3.12 (gestito automaticamente da `uv`)
- [`uv`](https://docs.astral.sh/uv/) 0.11 o successivo
- Docker (per la build dell'immagine di distribuzione)

## Setup locale

```bash
# Installazione uv (se non presente)
python -m pip install --user uv

# Python 3.12 gestito da uv
uv python install 3.12

# Creazione venv + installazione dipendenze (prod + dev)
uv sync

# Installazione browser Chromium per Playwright
uv run playwright install chromium
```

## Uso

```bash
# Esecuzione di un BOT (implementazione in corso)
uv run waf-bots --bot bot-1-dos --duration 60 --concurrency 4

# Elenco dei BOT supportati
uv run waf-bots --help
```

Con Docker:

```bash
docker build -t waf-bots:dev .
docker run --rm waf-bots:dev --bot bot-1-dos --duration 60
```

## Sviluppo

```bash
# Lint + format
uv run ruff check --fix
uv run ruff format

# Type check
uv run mypy

# Test
uv run pytest

# Hook pre-commit (una tantum)
uv run pre-commit install
```

## Struttura

```
.
├── memory/                 # Knowledge base operativa (schema 07)
├── src/waf_bots/
│   ├── cli.py              # Entry point CLI
│   ├── bots/               # Un modulo per BOT (dos, ato, registration, content/price scraping)
│   └── common/             # Logger JSON, client httpx, browser Playwright, WAF signals, reporter
├── tests/                  # Unit + smoke
├── Dockerfile              # Immagine singola py3.12-slim + Playwright
├── pyproject.toml          # Metadata progetto + config tool (ruff, mypy, pytest)
└── .pre-commit-config.yaml # Hook: ruff, mypy, check comuni
```

## BOT

| BOT | Categoria WAF | Tipo client | Stato |
|---|---|---|---|
| BOT-1 | Denial of Service | HTTP async | stub |
| BOT-2 | Account Takeover | HTTP async | stub |
| BOT-3 | Creazione account automatizzata | Browser (Playwright) | stub |
| BOT-4 | Content Scraping | Browser (Playwright) | stub |
| BOT-5 | Price Scraping | Browser (Playwright) | stub |

## Prerequisiti bloccanti

Prima di eseguire contro l'ambiente reale:

1. Verifica con il SOC che l'IP esecutore NON sia in whitelist WAF.
2. Ottenimento delle credenziali di test collaudo (Keycloak realm `AD-Arte-visitors`).
3. Conferma degli endpoint di search per BOT-1.

Dettagli e stato aggiornato in [`memory/05_quirks.md`](memory/05_quirks.md).

## Licenza

Proprietary - Prisma S.r.l.
