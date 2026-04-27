#!/usr/bin/env bash
# configure-linode-cli.sh
#
# Loads the Linode PAT from the operator's Obsidian vault lockbox into the
# current shell as `LINODE_CLI_TOKEN`. Avoids pasting the token in chat,
# in shell history, or in environment files synced to cloud storage.
#
# Lockbox location: $OBSIDIAN_VAULT/02_Areas/_secrets/linode.md
# Expected line in the lockbox: `token: <pat>` under a fenced code block or
# a YAML key. The script greps the first 64-hex-char token-shaped string
# inside the file.
#
# Usage:
#   source ./scripts/configure-linode-cli.sh
#   python -m linodecli profile view --json | head -1
#
# Notes:
#   - The script must be `source`d (not executed in a subshell), otherwise
#     the env export is lost.
#   - On Windows + Git Bash the vault path is usually
#     `C:/Users/<user>/Vault`. Set OBSIDIAN_VAULT in advance if non-default.

set -euo pipefail

VAULT="${OBSIDIAN_VAULT:-$HOME/Vault}"
if [[ "$OSTYPE" == msys* || "$OSTYPE" == cygwin* ]]; then
  VAULT="${OBSIDIAN_VAULT:-/c/Users/$USER/Vault}"
fi

LOCKBOX="$VAULT/02_Areas/_secrets/linode.md"

if [ ! -f "$LOCKBOX" ]; then
  echo "ERROR: lockbox not found at $LOCKBOX" >&2
  return 1 2>/dev/null || exit 1
fi

# Match a 64-char hex string. Linode PATs are lowercase hex.
TOKEN="$(grep -oE '[a-f0-9]{64}' "$LOCKBOX" | head -n1 || true)"

if [ -z "$TOKEN" ]; then
  echo "ERROR: no 64-hex-char token found in $LOCKBOX" >&2
  echo "       expected a line like 'token: <pat>' or a fenced code block with the PAT" >&2
  return 1 2>/dev/null || exit 1
fi

export LINODE_CLI_TOKEN="$TOKEN"
echo "OK: LINODE_CLI_TOKEN set (token length=${#TOKEN}, source=$LOCKBOX)"
echo "Verify with:  python -m linodecli profile view --json | head -1"
