# KNOWN DEPENDENCIES

## Stack applicativo BOT

| Dipendenza | Scopo | Vincolo |
|---|---|---|
| Python 3.12 | Runtime | Versione fissata nel Dockerfile. In locale Samuele c'e' 3.11.9, compatibile per sviluppo |
| httpx | HTTP client async | Per BOT-1 (DoS) e BOT-2 (ATO). Supporto HTTP/2 e timeout fini |
| Playwright (Chromium headless) | Browser automation | Per BOT-3 (registration), BOT-4 (content scraping), BOT-5 (price scraping) |
| pytest | Orchestratore esecuzione e raccolta esiti | Integrazione con logger strutturato |
| logging JSON | Output strutturato | Formato da definire, compatibile con parser Markdown reporter |
| Docker | Packaging | Immagine singola, parametrizzata da flag di lancio |

## Dipendenze tra i BOT

- **Codice condiviso**: BOT-4 e BOT-5 hanno base Playwright comune (navigazione, Chromium setup, waiter) da fattorizzare in modulo `common/browser.py`.
- **Codice condiviso 2**: BOT-1 e BOT-2 condividono HTTP client factory httpx async, retry policy, parser risposta WAF.
- **Reporter**: tutti i BOT producono lo stesso schema JSON per consolidamento.

## Dipendenze lato backend (Ad Arte)

Informazione utile per interpretare fallimenti non-WAF durante i test:

- **Keycloak** e' SPOF per login (BOT-2) e registration (BOT-3). Se Keycloak e' down nel collaudo, i BOT segnalano errori che non sono frutto del WAF.
- **integration-app-web** (Spring Boot) espone i path `/app/api/...` target di scraping e DoS.
- **cms-ms** (Django) espone `/cms-ms/api/public/cached/...` (monitor Datadog noto su `museum`, `museum-with-e-ticketing`, `museum/{id}`, `overview`).
- **ssot-*** e **aimusei-be**: presenti in elenco swagger ma non target diretto dei 5 BOT allo stato attuale. Possono essere coinvolti indirettamente.

## Dipendenze esterne del processo di test

- **SOC Ad Arte**: dipendenza bloccante su prerequisito whitelist WAF e su fornitura log FortiGate a test concluso.
- **Cliente**: dipendenza bloccante su fornitura credenziali test e lista esatta endpoint (soprattutto "pagine di ricerca" per BOT-1).
