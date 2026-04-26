#!/usr/bin/env bash
# teardown-fleet.sh
#
# Deletes all Linode VMs tagged $TAG (default: antibot).
# Two-stage: dry-run (default) prints the list, then explicit --yes deletes.
#
# Required env:
#   LINODE_CLI_TOKEN
# Optional env:
#   TAG               default: antibot
#
# Usage:
#   ./scripts/teardown-fleet.sh           # dry-run, prints affected VMs
#   ./scripts/teardown-fleet.sh --yes     # actually delete

set -euo pipefail
: "${LINODE_CLI_TOKEN:?missing - export from your lockbox before running}"

TAG="${TAG:-antibot}"
YES=0
[ "${1:-}" = "--yes" ] && YES=1

LCLI() { python -m linodecli "$@"; }

mapfile -t VICTIMS < <(
  LCLI linodes list --json | python -c "
import json, sys, os
tag=os.environ['T']
for v in json.load(sys.stdin):
    if tag in v.get('tags', []):
        print(f\"{v['id']}|{v['label']}|{v['type']}|{v['region']}|{v['status']}\")
" T="$TAG"
)

if [ "${#VICTIMS[@]}" -eq 0 ]; then
  echo "[teardown] no VMs with tag '$TAG'"
  exit 0
fi

echo "[teardown] tag='$TAG', ${#VICTIMS[@]} VM(s):"
printf '  %s\n' "${VICTIMS[@]}"

if [ "$YES" -eq 0 ]; then
  echo
  echo "[teardown] dry-run. To delete, re-run with --yes"
  exit 0
fi

for line in "${VICTIMS[@]}"; do
  id="${line%%|*}"
  echo "[delete] linode id=$id"
  LCLI linodes delete "$id"
done

echo "[teardown] done"
