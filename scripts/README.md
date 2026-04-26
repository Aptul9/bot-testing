# scripts/

Operational scripts for the antibot Linode fleet. Manual end-to-end flow:

```
[bootstrap-vm.sh]   uploaded once as a Linode StackScript -> id captured
        |
        v
[provision-fleet.sh]   creates 5 VMs (2 HTTP + 3 browser), attaches StackScript
        |
        v
[VMs run StackScript on first boot]   Docker + git + clone repo + build image
        |
        v
[BOT run]   ssh root@<ip> docker run --rm waf-bots:dev --bot ... --no-dry-run
        |
        v
[collect-reports.sh]   scp JSON from each VM, consolidate into Markdown
        |
        v
[teardown-fleet.sh]   delete all VMs tagged 'antibot'
```

## Prerequisites

- `python -m pip install --user linode-cli` (one-time)
- `LINODE_CLI_TOKEN` in env from `02_Areas/_secrets/linode.md` lockbox
- SSH key uploaded to Linode account: see `custom-instructions/linode.md` § 10
- Credit card on Linode account (or invoiced billing pre-confirmed)
- Pre-mortem document signed off (especially for BOT-1 DoS): `docs/pre-mortem-bot-1.md`

## One-time setup

```bash
# 1. SSH key (skip if already exists in your account)
ssh-keygen -t ed25519 -C "claude@waf-bots" -f ~/.ssh/linode_ed25519 -N ""
python -m linodecli sshkeys create \
  --label "claude-waf-bots-2026-04" \
  --ssh_key "$(cat ~/.ssh/linode_ed25519.pub)"

# 2. Upload bootstrap script as StackScript
python -m linodecli stackscripts create \
  --label waf-bots-bootstrap \
  --description "Install Docker + clone bot-testing repo + build image" \
  --images linode/ubuntu24.04 \
  --is_public false \
  --script "$(cat scripts/bootstrap-vm.sh)" \
  --json | python -c "import json,sys; print('STACKSCRIPT_ID=', json.load(sys.stdin)[0]['id'])"
# capture the id, export it before running provision-fleet.sh
```

## Run

```bash
export LINODE_CLI_TOKEN=...      # from lockbox
export STACKSCRIPT_ID=...        # from setup above
export REGION=nl-ams             # or de-fra-2; do NOT use it-mil
export SSHKEY_LABEL=claude-waf-bots-2026-04

./scripts/provision-fleet.sh

# wait 3-5 min for boot + StackScript completion. Then check a VM:
ssh -i ~/.ssh/linode_ed25519 root@<ipv4> "tail -5 /var/log/stackscript.done"

# launch a BOT on each VM (example for BOT-1 DoS, requires WAF_BOTS_ALLOW_DOS=true)
for ip in $(python -m linodecli linodes list --json | python -c "
import json, sys
for v in json.load(sys.stdin):
    if 'antibot' in v.get('tags', []) and 'http' in v['label']:
        print(v['ipv4'][0])
"); do
  ssh -i ~/.ssh/linode_ed25519 -o StrictHostKeyChecking=accept-new "root@$ip" \
    "docker run --rm -e WAF_BOTS_ALLOW_DOS=true waf-bots:dev \
       --bot bot-1-dos --duration 60 --concurrency 4 --no-dry-run \
       --output /tmp/report.json"
done

./scripts/collect-reports.sh
# -> reports/local/consolidated.md
```

## Teardown

```bash
./scripts/teardown-fleet.sh        # dry-run, prints affected VMs
./scripts/teardown-fleet.sh --yes  # actually delete
```

## Safety

- `provision-fleet.sh` is idempotent (skips VMs whose label already exists)
- `teardown-fleet.sh` defaults to dry-run; `--yes` required to actually delete
- BOT-1 DoS requires `WAF_BOTS_ALLOW_DOS=true` env var even at the BOT level (defence in depth)
- Pre-mortem document mandatory before any `--no-dry-run` BOT-1 run, per `08_advanced_safety_time_and_pipelines.md` § 2

## Reference

- Full guide: `custom-instructions/linode.md`
- Project KB: `01_Projects/antibot.md` in the operator's Obsidian vault
- Lockbox: `02_Areas/_secrets/linode.md`
