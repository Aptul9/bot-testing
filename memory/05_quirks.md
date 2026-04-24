# QUIRKS AND LANDMINES

## Prerequisiti bloccanti aperti (stato 2026-04-24)

| # | Prerequisito | Owner | Stato |
|---|---|---|---|
| 1 | IP esecutore NON presente in whitelist WAF Ad Arte | SOC | Da verificare prima di ogni run reale |
| 2 | Credenziali test collaudo (login, reset password, registration) | Cliente | Non fornite |
| 3 | Lista esatta endpoint "pagine di ricerca" per BOT-1 DoS | Cliente | Non presente negli Excel forniti |
| 4 | Scope "locale": se i BOT colpiscono il WAF di collaudo dalla macchina Samuele o solo dry-run | Utente | Da confermare |
| 5 | Branching strategy (main diretto o feature + PR) | Utente | Default provvisorio: main |
| 6 | Python 3.12 in locale (installazione richiesta?) oppure sviluppo su 3.11 + release solo Docker 3.12 | Utente | Default provvisorio: 3.11 locale, 3.12 in Docker |

L'esecuzione dei BOT contro il WAF non puo' partire finche' i prerequisiti 1, 2, 3 non sono chiusi.

## Rischi noti (dalla specifica, tabella R1-R5)

| ID | Rischio | Mitigazione |
|---|---|---|
| R1 | IP sorgente gia' segnalati come malevoli in liste pubbliche | Selezione IP puliti, monitoring del primo response |
| R2 | Soglia WAF molto alta: i BOT non innescano alcuna protezione | Incremento progressivo di concorrenza e durata |
| R3 | Blocco generalizzato del servizio Ad Arte se il DoS impatta backend condivisi | **Avvio a concorrenza bassa, escalation graduale** |
| R4 | Consumo RAM elevato di Playwright su VM piccole | Minimo 8 GB RAM per BOT browser-based (non rilevante in locale se macchina sufficiente) |
| R5 | IP esecutori coincidono con whitelist gia' configurata sul WAF | Incrocio preventivo con SOC |

## Vincoli comportamentali dei BOT

- I BOT devono essere **palesemente riconoscibili come automation**. NO tecniche di evasione.
  - `navigator.webdriver = true` (default Playwright, da non mascherare)
  - Headless evidente (nessun fingerprinting spoofing)
  - User-Agent default o bot-like esplicito
  - No delay "umani"
  - Pattern sequenziale, non randomizzato
  - Nessuna rotazione di header, cookie, fingerprint
- Il test verifica la **baseline di detection**, non la resistenza del WAF ad attaccanti sofisticati.
- Tecniche di evasione (stealth plugin, residential proxy, TLS fingerprint spoofing) sono fuori scope.

## Operazione critica: BOT-1 DoS

- Rischio reale di impatto su servizio Ad Arte se il backend condiviso cade.
- Procedura richiesta:
  1. Avvio con concorrenza minima (es. 1-5 richieste/sec).
  2. Monitoring risposta (codici, latenza, errori upstream).
  3. Escalation a gradini, solo se il WAF non ha ancora risposto.
  4. Stop immediato se si osservano errori 5xx lato backend non imputabili al WAF.
- Pre-mortem e rollback richiesti prima di ogni run BOT-1, come da regola 08 sez. 2.

## Sicurezza repo

- Repo `Aptul9/bot-testing` su GitHub: **deve restare privato** finche' memory/ contiene riferimenti operativi non banali.
- Qualsiasi credenziale, token, refresh token, chiave API: NON nei file tracciati. Solo in `memory/secrets.md` (gitignored).
- Prima di ogni commit, verificare con `git diff --cached` che non siano incluse stringhe segrete.

## Ambigui gia' chiariti

- Memoria e' nel repo (non in `~/Desktop/memory/` come da schema 07 standard). Decisione utente 2026-04-24 per consentire continuita' multi-chat multi-persona. Il tradeoff (repo privato obbligatorio, split secrets) e' esplicitato in `00_index.md`.
