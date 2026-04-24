# MEMORY INDEX

## Scopo

Knowledge base operativa del progetto `bot-testing` (validazione WAF Fortinet antiBot Ad Arte). Schema basato su `07_memory_and_operational_context.md` delle istruzioni operative.

Doppio obiettivo:
- **Continuità cross-session**: una nuova chat deve poter ripartire da zero leggendo questa cartella.
- **Collaborazione multi-persona**: chiunque subentri ricostruisce il contesto senza dipendere da conoscenza implicita di chi ha iniziato.

Se un file di questa cartella non è sufficiente a ricostruire il contesto, è incompleto e va aggiornato.

## Struttura

| File | Sezione schema 07 | Contenuto |
|---|---|---|
| `00_index.md` | - | Indice e linee guida d'uso |
| `01_infrastructure.md` | [INFRASTRUCTURE] | Architettura, endpoint base, microservizi, swagger |
| `02_operations_access.md` | [OPERATIONS & ACCESS] | Come raggiungere gli ambienti, credenziali di riferimento (non i valori) |
| `03_pipelines.md` | [PIPELINES & CI/CD] | Repo, branching, CI/CD |
| `04_dependencies.md` | [KNOWN DEPENDENCIES] | Stack tecnico, dipendenze tra servizi |
| `05_quirks.md` | [QUIRKS & LANDMINES] | Prerequisiti bloccanti, workaround, rischi noti |
| `06_changelog.md` | [CHANGELOG] | Timeline operativa |
| `07_objectives.md` | contesto | Obiettivo tecnico e di business, matrice BOT |
| `08_endpoints.md` | contesto | Elenco completo endpoint target per categoria protezione WAF |
| `secrets.md.example` | - | Template per credenziali (il file reale `secrets.md` è in .gitignore) |

## Regole di manutenzione

- Aggiornare **a ogni** nuova informazione operativa rilevante (nuovo endpoint, anomalia, decisione, workaround, credenziale aggiunta/revocata).
- I timestamp nel changelog seguono il formato `[YYYY-MM-DD HH:MM:SS]`.
- Stile impersonale e passivo. No emoji. No em dash. No prima persona.
- Le credenziali in chiaro NON vanno in questi file. Vanno in `secrets.md` locale (gitignored).
- Il repo è privato su GitHub. Se torna pubblico, rimuovere/mascherare `secrets.md.example` e ogni riferimento a nome utente reale, prima del push.

## Come orientarsi da nuova chat

1. Leggere `07_objectives.md` per capire cosa stiamo facendo.
2. Leggere `01_infrastructure.md` + `08_endpoints.md` per il target tecnico.
3. Leggere `05_quirks.md` per sapere cosa NON fare e cosa è bloccante.
4. Leggere `06_changelog.md` per l'ultimo stato operativo.
5. Se serve eseguire contro ambiente: leggere `02_operations_access.md` + caricare `secrets.md` locale.
