"""BOT-3 Automated account creation. Target: signup / registration page.

The Keycloak signup endpoint URL pattern is not the same as the API base URL.
The bot looks at env var `WAF_BOTS_KEYCLOAK_BASE_URL` to find the Keycloak host;
if unset it falls back to the api base_url passed by the CLI, which is OK in
dry-run but will likely 404 against the real target.

Open question for the client (see [[antibot#Asks - Client (credentials)]]):
  - confirm Keycloak base URL on collaudo
  - confirm whether visitor self-registration is exposed (no admin bearer)
  - if so, give the exact signup URL and any required form fields

Until that question is answered, `paths` carries best-effort guesses based on
the standard Keycloak realm layout.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import ClassVar
from urllib.parse import urljoin

from waf_bots.bots.browser_bot import BrowserBot

KEYCLOAK_BASE_URL_ENV = "WAF_BOTS_KEYCLOAK_BASE_URL"

# Placeholder Keycloak signup paths. Standard Keycloak layout for a realm
# named AD-Arte-visitors. Confirm with client (see Asks section in vault).
_REALM = "AD-Arte-visitors"


class RegistrationBot(BrowserBot):
    name = "bot-3-registration"

    paths: ClassVar[Sequence[str]] = (
        f"/realms/{_REALM}/protocol/openid-connect/registrations",
        f"/realms/{_REALM}/login-actions/registration",
    )

    def _keycloak_base_url(self) -> str:
        return os.environ.get(KEYCLOAK_BASE_URL_ENV) or self.base_url

    def _next_url(self, sequence: int) -> str:
        path = self.paths[(sequence - 1) % len(self.paths)]
        base = self._keycloak_base_url()
        if not base.endswith("/") and not path.startswith("/"):
            return f"{base}/{path}"
        return urljoin(base + ("" if base.endswith("/") else "/"), path.lstrip("/"))
