#!/usr/bin/env bash
# seed-test-visitors.sh
#
# One-shot helper: provision N visitor users in Keycloak realm AD-Arte-visitors
# via the admin REST API. Output: a list of {username, password} pairs to be
# pasted into the operator's lockbox `02_Areas/_secrets/antibot.md` and then
# consumed by BOT-2 ATO via WAF_BOTS_ATO_USERNAME / WAF_BOTS_ATO_PASSWORD
# (one user per BOT-2 instance).
#
# Required env (from `[[_secrets/antibot]]` lockbox):
#   WAF_BOTS_KEYCLOAK_BASE_URL       e.g. https://login-coll.museiitaliani.it
#   WAF_BOTS_KEYCLOAK_REALM          AD-Arte-visitors
#   WAF_BOTS_KEYCLOAK_ADMIN_CLIENT_ID  admin-cli
#   WAF_BOTS_KEYCLOAK_ADMIN_USER     <admin user from operator's lockbox>
#   WAF_BOTS_KEYCLOAK_ADMIN_PASSWORD <admin password from operator's lockbox>
# Optional:
#   COUNT                            default 2
#   USERNAME_PREFIX                  default waf-test-visitor
#
# Usage:
#   export $(grep -v '^#' .env.real | xargs)   # or source configure-*.sh helper
#   ./scripts/seed-test-visitors.sh
#
# Output goes to stdout as JSON lines (one user per line). Save the output to
# the lockbox; do not commit it.

set -euo pipefail

: "${WAF_BOTS_KEYCLOAK_BASE_URL:?missing}"
: "${WAF_BOTS_KEYCLOAK_REALM:?missing}"
: "${WAF_BOTS_KEYCLOAK_ADMIN_CLIENT_ID:?missing}"
: "${WAF_BOTS_KEYCLOAK_ADMIN_USER:?missing}"
: "${WAF_BOTS_KEYCLOAK_ADMIN_PASSWORD:?missing}"

COUNT="${COUNT:-2}"
PREFIX="${USERNAME_PREFIX:-waf-test-visitor}"

KC="$WAF_BOTS_KEYCLOAK_BASE_URL"
REALM="$WAF_BOTS_KEYCLOAK_REALM"

# 1. admin token
TOKEN_JSON="$(curl -fsSL -X POST \
  "$KC/realms/$REALM/protocol/openid-connect/token" \
  -d "client_id=$WAF_BOTS_KEYCLOAK_ADMIN_CLIENT_ID" \
  -d "username=$WAF_BOTS_KEYCLOAK_ADMIN_USER" \
  -d "password=$WAF_BOTS_KEYCLOAK_ADMIN_PASSWORD" \
  -d "grant_type=password")"

TOKEN="$(echo "$TOKEN_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')"

if [ -z "$TOKEN" ]; then
  echo "ERROR: failed to obtain admin token" >&2
  exit 1
fi

# 2. create COUNT users, print credentials
for i in $(seq 1 "$COUNT"); do
  STAMP="$(date -u +%s)"
  USERNAME="${PREFIX}-${STAMP}-${i}"
  EMAIL="${USERNAME}@example.invalid"
  # 16-byte URL-safe random password
  PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')"

  PAYLOAD="$(python3 -c "
import json, sys
print(json.dumps({
  'username': sys.argv[1],
  'email': sys.argv[2],
  'enabled': True,
  'emailVerified': True,
  'firstName': 'WAF',
  'lastName': 'Test',
  'credentials': [{'type':'password','value':sys.argv[3],'temporary':False}]
}))
" "$USERNAME" "$EMAIL" "$PASSWORD")"

  HTTP_CODE="$(curl -s -o /dev/null -w '%{http_code}' -X POST \
    "$KC/admin/realms/$REALM/users" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")"

  if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "204" ]; then
    python3 -c "
import json, sys
print(json.dumps({'username': sys.argv[1], 'email': sys.argv[2], 'password': sys.argv[3], 'http_code': int(sys.argv[4])}))
" "$USERNAME" "$EMAIL" "$PASSWORD" "$HTTP_CODE"
  else
    echo "ERROR: user $USERNAME creation failed with HTTP $HTTP_CODE" >&2
  fi
done
