# PIPELINES AND CI/CD

## Stato attuale

Nessuna pipeline CI/CD attiva. Esplicitamente fuori scope per questa iniziativa (vedi `07_objectives.md` sezione "Out of scope").

## Repository

| Campo | Valore |
|---|---|
| URL | `https://github.com/Aptul9/bot-testing` |
| Default branch | `main` |
| Visibilita' | Privato (cambio richiesto il 2026-04-24 prima del primo push) |
| Owner git user locale | `Aptul` |

## Branching strategy

Da consolidare con l'owner. Default provvisorio:
- Commit diretti su `main` durante la fase di bootstrap (repo vuoto, nessuna production line).
- Da fase BOT-1 in poi valutare feature branch + PR per separare lo sviluppo di ogni BOT.

## Build artifact

- Singola immagine Docker `waf-bots` contenente tutti i BOT.
- Build eseguita localmente o sulla VM. Nessun registry esterno previsto.
- Tag immagine: TBD (es. semver `v0.1.0` oppure data).
