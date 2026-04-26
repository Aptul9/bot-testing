# waf-bots

BOT client for validation of the antiBot policies on the Fortinet FortiGate WAF in the Ad Arte collaudo environment.

Operational context, objectives, BOT matrix, endpoint targets, risks, prerequisites, decisions and timeline live in the operator's **Obsidian vault**: project page `01_Projects/antibot.md`. Credentials live in the lockbox `02_Areas/_secrets/antibot.md` (excluded from any sync). Repo and vault are separated by design: the repo holds code only, the vault holds the knowledge base.

If you onboard without the vault: ask the project owner for the two vault files (`antibot.md` and `_secrets/antibot.md`).

## Requirements

- Python 3.12 (managed automatically by `uv`)
- [`uv`](https://docs.astral.sh/uv/) 0.11 or later
- Docker (for the distribution image build)
- Linode CLI (for fleet provisioning, optional for local dev)

## Local setup

```bash
# Install uv (if missing)
python -m pip install --user uv

# Python 3.12 managed by uv
uv python install 3.12

# Create venv + install deps (prod + dev)
uv sync

# Install Chromium for Playwright (needed by BOT-3/4/5)
uv run playwright install chromium
```

## Local usage (dev / dry-run)

```bash
# Run a BOT in dry-run mode (default - no real HTTP traffic)
uv run waf-bots --bot bot-1-dos --duration 60 --concurrency 4

# List supported BOTs and flags
uv run waf-bots --help
```

With Docker:

```bash
docker build -t waf-bots:dev .
docker run --rm waf-bots:dev --bot bot-1-dos --duration 60
```

## Real run (collaudo target)

Real run requires the prerequisites tracked in `01_Projects/antibot.md` `## Blockers` (vault) to be closed:

1. SOC confirmed executor IPs NOT in WAF whitelist
2. Client provided test credentials (Keycloak realm `AD-Arte-visitors`)
3. Client confirmed search endpoints list (for BOT-1 DoS)
4. User confirmed local scope vs Linode fleet

For the Linode fleet path (recommended once prereqs unlocked):

```bash
# 1. Token from lockbox
export LINODE_CLI_TOKEN="<from 02_Areas/_secrets/linode.md>"

# 2. Provision (idempotent, safe to re-run)
export STACKSCRIPT_ID=<id from one-time setup>
export REGION=nl-ams
./scripts/provision-fleet.sh

# 3. Wait 3-5 min for cloud-init / StackScript completion on each VM

# 4. Trigger BOT runs (see scripts/README.md for the full per-VM loop)

# 5. Collect + consolidate reports
./scripts/collect-reports.sh

# 6. Teardown
./scripts/teardown-fleet.sh --yes
```

Detailed flow + one-time setup steps in [`scripts/README.md`](scripts/README.md).

Comprehensive Linode reference (regions, types, pricing, StackScripts, lessons learned): `custom-instructions/linode.md` in the operational instructions.

**Pre-mortem mandatory for BOT-1 DoS real runs**: see [`docs/pre-mortem-bot-1.md`](docs/pre-mortem-bot-1.md).

## Development

```bash
# Lint + format
uv run ruff check --fix
uv run ruff format

# Type check
uv run mypy

# Tests
uv run pytest

# Pre-commit hooks (one-time)
uv run pre-commit install
```

## Repo structure

```
.
├── src/waf_bots/
│   ├── cli.py              # CLI entry point
│   ├── bots/               # one module per BOT (dos, ato, registration, content/price scraping)
│   │                       # plus base.py, http_bot.py, browser_bot.py
│   └── common/             # JSON logger, httpx client, Playwright browser, WAF signals, reporter
├── tests/                  # unit + smoke
├── scripts/                # Linode fleet provisioning + teardown + collection
├── docs/                   # pre-mortems, architecture notes
├── Dockerfile              # python:3.12-slim + Playwright
├── pyproject.toml          # project metadata + tool config (ruff, mypy, pytest)
├── .env.example            # consumed env vars schema
├── .github/workflows/ci.yml
└── .pre-commit-config.yaml # ruff, mypy, common checks
```

Knowledge base: in the operator's Obsidian vault (see introduction).

## BOT status

| BOT | WAF category | Client type | Status |
|---|---|---|---|
| BOT-1 | Denial of Service | HTTP async (httpx) | scaffold + dry-run safe (real run requires `WAF_BOTS_ALLOW_DOS=true`) |
| BOT-2 | Account Takeover | HTTP async (httpx) | scaffold + dry-run safe |
| BOT-3 | Automated account creation | Browser (Playwright) | stub - needs admin Keycloak |
| BOT-4 | Content Scraping | Browser (Playwright) | scaffold + dry-run safe |
| BOT-5 | Price Scraping | Browser (Playwright) | scaffold + dry-run safe |

## Safety defaults

- `--dry-run` is the default for every BOT. Real traffic requires `--no-dry-run`
- BOT-1 DoS additionally requires `WAF_BOTS_ALLOW_DOS=true` env var on the run host
- Teardown script (`scripts/teardown-fleet.sh`) defaults to dry-run; `--yes` required to delete VMs
- All fleet VMs are tagged `antibot` so teardown is precise

## License

Proprietary - Prisma S.r.l.
