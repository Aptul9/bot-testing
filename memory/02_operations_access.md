# OPERATIONS AND ACCESS

## Connettività verso collaudo

- Gli endpoint `api-coll.museiitaliani.it` sono pubblici. Non richiedono VPN per essere raggiunti dal client dei BOT.
- L'accesso alla console WAF FortiGate non è previsto da questo scope. Il SOC è il referente per estrazione log e verifiche whitelist.

## Credenziali

Le credenziali in chiaro NON vanno in questi file tracciati.

- Vedere `secrets.md.example` per il template richiesto.
- La copia reale `secrets.md` è in `.gitignore`. Chi subentra in un nuovo ambiente chiede il file all'owner e lo salva in `memory/secrets.md` localmente.
- Keycloak realm: `AD-Arte-visitors`. Servono almeno:
  - un utente visitor valido per login (BOT-2 ATO)
  - credenziali admin o service account Keycloak per registrazione utenti via `/admin/realms/.../users` (BOT-3)

## Esecuzione locale

| Componente | Versione di riferimento | Versione presente sulla macchina corrente |
|---|---|---|
| Python | 3.12 (nel Dockerfile) | 3.11.9 (Windows user Samuele) |
| Docker | non vincolato | 29.3.1 |
| httpx | ultima stabile | da installare |
| Playwright | ultima stabile | da installare (+ browser Chromium) |
| pytest | ultima stabile | da installare |

- Sul comando Python locale usare `python` (non `python3`). Solo su VM Linux remote si usa `python3`.
- Build e run dei BOT avviene via `docker build` + `docker run`. Lo sviluppo iterativo locale può usare venv con Python 3.11; la release finale gira con Python 3.12 nell'immagine.

## Comando di lancio previsto (da specifica)

```
docker run waf-bots --bot <nome> --duration <durata>
```

Dove `<nome>` ∈ {`bot-1-dos`, `bot-2-ato`, `bot-3-registration`, `bot-4-content-scraping`, `bot-5-price-scraping`}.

Parametri aggiuntivi da consolidare in implementazione:
- concorrenza (solo per BOT HTTP async)
- intensità (RPS)
- URL base override
- path file output JSON

## Referenti

| Ruolo | Referente | Responsabilità |
|---|---|---|
| Owner backend | Almaviva | Keycloak, ticketing, integration-app-web |
| Whitelist WAF | SOC | Garantire che gli IP esecutori NON siano in whitelist prima del test |
| Credenziali test collaudo | Cliente (Ad Arte) | Utenze per login, reset password, registrazione |
| Lista endpoint target | Cliente (Ad Arte) | Completamento endpoint per categoria (in particolare BOT-1 DoS su pagine di ricerca) |

## Report finale

- Output per BOT: JSON su stdout (logging strutturato).
- Consolidamento: report Markdown unico con tabella di sintesi per categoria, evidenze raccolte, conclusioni operative.
- Allegato atteso: export log FortiGate dalla finestra di esecuzione, fornito dal SOC a test concluso.
