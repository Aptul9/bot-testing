#!/usr/bin/env bash
# provision-fleet.sh
#
# Idempotent provisioning of the antibot Linode fleet.
# Reads LINODE_CLI_TOKEN from env (lockbox 02_Areas/_secrets/linode.md in the
# operator's Obsidian vault).
#
# Required env:
#   LINODE_CLI_TOKEN  Linode PAT
# Optional env:
#   REGION            Linode region id (default: nl-ams)
#   IMAGE             Linode image id (default: linode/ubuntu24.04)
#   SSHKEY_LABEL      Linode sshkeys label to embed (default: claude-waf-bots)
#   STACKSCRIPT_ID    StackScript id from `linode-cli stackscripts create`
#                     (uploaded once via scripts/bootstrap-vm.sh content)
#   TAG               Tag applied to all VMs (default: antibot)
#
# Usage:
#   export LINODE_CLI_TOKEN=...
#   export STACKSCRIPT_ID=12345
#   ./scripts/provision-fleet.sh
#
# The script SKIPS creation of any VM whose label already exists
# (so re-running after partial failure is safe).

set -euo pipefail

: "${LINODE_CLI_TOKEN:?missing - export from your lockbox before running}"

REGION="${REGION:-nl-ams}"
IMAGE="${IMAGE:-linode/ubuntu24.04}"
SSHKEY_LABEL="${SSHKEY_LABEL:-claude-waf-bots}"
STACKSCRIPT_ID="${STACKSCRIPT_ID:-}"
TAG="${TAG:-antibot}"

LCLI() { python -m linodecli "$@"; }

echo "[provision] region=$REGION image=$IMAGE sshkey=$SSHKEY_LABEL stackscript=${STACKSCRIPT_ID:-<none>} tag=$TAG"

# fleet definition: label, type
FLEET=(
  "waf-bot-http-01:g6-standard-1"
  "waf-bot-http-02:g6-standard-1"
  "waf-bot-browser-01:g6-standard-2"
  "waf-bot-browser-02:g6-standard-2"
  "waf-bot-browser-03:g6-standard-2"
)

create_one() {
  local label="$1" type="$2"
  if LCLI linodes list --json | python -c "
import json, sys, os
target=os.environ['L']
data=json.load(sys.stdin)
sys.exit(0 if any(v.get('label')==target for v in data) else 1)
" L="$label"; then
    echo "[skip] $label exists"
    return 0
  fi

  local args=(
    linodes create
    --label "$label"
    --region "$REGION"
    --type "$type"
    --image "$IMAGE"
    --root_pass "$(openssl rand -base64 24)"
    --authorized_users "$SSHKEY_LABEL"
    --tags "$TAG"
    --booted true
  )
  if [ -n "$STACKSCRIPT_ID" ]; then
    args+=( --stackscript_id "$STACKSCRIPT_ID" )
  fi
  echo "[create] $label ($type)"
  LCLI "${args[@]}" --json | python -c "
import json, sys
v=json.load(sys.stdin)
if isinstance(v, list): v=v[0]
print(f\"  id={v['id']} ipv4={v['ipv4'][0]} status={v['status']}\")
"
}

for entry in "${FLEET[@]}"; do
  IFS=':' read -r label type <<< "$entry"
  create_one "$label" "$type"
done

echo "[provision] done. Wait ~3-5 min for cloud-init / StackScript to finish."
echo "[provision] tail /var/log/stackscript.log on a VM to verify boot success."
