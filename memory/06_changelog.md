# CHANGELOG

Formato: `[YYYY-MM-DD HH:MM:SS] Evento`.

---

## [2026-04-24]

- Kickoff sessione su progetto `bot-testing`.
- Analisi documento requisiti `Bot Testing Ad Arte_v1.2.docx`: obiettivo, 5 categorie BOT, stack tecnico, rischi, pianificazione.
- Analisi Excel `URL-WAF AntiBoT.xlsx` e `API_antiBot_AdArte.xlsx`: matrice endpoint target per categoria di protezione + endpoint Keycloak e ticketing.
- Lettura istruzioni operative (`C:\Users\Samuele\Downloads\istruzioni\`) files `00` - `11`.
- Decisione utente: esecuzione **locale** inizialmente, no VM Linode.
- Decisione utente: knowledge base **nel repository** (anziche' `~/Desktop/memory/`) per consentire continuita' cross-chat e collaborazione multi-persona.
- Decisione utente: repo GitHub privatizzato per contenere memory/ senza esporre dati operativi.
- Setup struttura `memory/` nel repo secondo schema `07_memory_and_operational_context.md` adattato:
  - `00_index.md` indice e regole
  - `01_infrastructure.md` endpoint, swagger, microservizi
  - `02_operations_access.md` come raggiungere l'ambiente, referenti, pattern secrets.md
  - `03_pipelines.md` repo, branching provvisorio, CI/CD out-of-scope
  - `04_dependencies.md` stack e dipendenze tra servizi
  - `05_quirks.md` prerequisiti bloccanti aperti e rischi noti
  - `06_changelog.md` questo file
  - `07_objectives.md` obiettivo tecnico, matrice BOT, out-of-scope
  - `08_endpoints.md` elenco completo endpoint target per categoria WAF
  - `secrets.md.example` template credenziali
- `.gitignore` creato per escludere `memory/secrets.md` e artefatti locali.
- Primo commit locale su `main` (repo era senza commit prima). Push eseguito dopo conferma privatizzazione repo.

Prerequisiti bloccanti aperti (vedi `05_quirks.md`): whitelist IP, credenziali test, lista endpoint search BOT-1, conferma scope locale, branching, Python 3.12 locale.
