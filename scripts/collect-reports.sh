#!/usr/bin/env bash
# collect-reports.sh
#
# After a BOT run on the fleet, collects per-VM JSON reports via SSH and
# consolidates them into a single Markdown report.
#
# Assumes:
#   - Each VM ran `docker run --rm waf-bots:dev --bot <name> --duration N
#     --output /tmp/report.json --no-dry-run ...` and produced /tmp/report.json
#   - SSH access via the key uploaded at provisioning time
#   - The local box has Python 3.12 venv with the waf_bots package installed
#     (uv run python ... or activated venv)
#
# Required env:
#   LINODE_CLI_TOKEN
# Optional env:
#   TAG               filter VMs by tag (default: antibot)
#   SSH_KEY           path to private SSH key (default: ~/.ssh/linode_ed25519)
#   OUT_DIR           local dir for collected JSON (default: ./reports/local)
#   MARKDOWN_OUT      path for consolidated Markdown (default: $OUT_DIR/consolidated.md)
#
# Usage:
#   ./scripts/collect-reports.sh

set -euo pipefail
: "${LINODE_CLI_TOKEN:?missing}"

TAG="${TAG:-antibot}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/linode_ed25519}"
OUT_DIR="${OUT_DIR:-./reports/local}"
MARKDOWN_OUT="${MARKDOWN_OUT:-$OUT_DIR/consolidated.md}"

mkdir -p "$OUT_DIR"

LCLI() { python -m linodecli "$@"; }

mapfile -t TARGETS < <(
  LCLI linodes list --json | python -c "
import json, sys, os
tag=os.environ['T']
for v in json.load(sys.stdin):
    if tag in v.get('tags', []) and v.get('status')=='running':
        print(f\"{v['label']}|{v['ipv4'][0]}\")
" T="$TAG"
)

if [ "${#TARGETS[@]}" -eq 0 ]; then
  echo "[collect] no running VMs with tag '$TAG'"
  exit 0
fi

echo "[collect] ${#TARGETS[@]} VM(s) to scrape"
for entry in "${TARGETS[@]}"; do
  IFS='|' read -r label ip <<< "$entry"
  out="$OUT_DIR/${label}.json"
  echo "[scp] $label ($ip) -> $out"
  scp -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new \
    "root@${ip}:/tmp/report.json" "$out" 2>/dev/null \
    || echo "  (failed: maybe BOT did not write /tmp/report.json yet)"
done

echo "[consolidate] -> $MARKDOWN_OUT"
python - <<PY
import json, glob, os, sys
from waf_bots.common.reporter import RunReport, consolidate

reports = []
for path in sorted(glob.glob("$OUT_DIR/*.json")):
    with open(path, "r", encoding="utf-8") as f:
        try:
            d = json.load(f)
        except json.JSONDecodeError:
            continue
    reports.append(RunReport(
        bot=d["bot"],
        started_at=d["started_at"],
        ended_at=d["ended_at"],
        duration_s=d["duration_s"],
        requests_total=d["requests_total"],
        first_block_after_s=d["first_block_after_s"],
        first_block_after_requests=d["first_block_after_requests"],
        signals_count=d.get("signals_count", {}),
        metadata=d.get("metadata", {}),
    ))

if not reports:
    print("no JSON reports parsed", file=sys.stderr)
    sys.exit(0)

with open("$MARKDOWN_OUT", "w", encoding="utf-8") as f:
    f.write(consolidate(reports, title="Antibot fleet run report"))
print(f"wrote {len(reports)} report(s) to $MARKDOWN_OUT")
PY
