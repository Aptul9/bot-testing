# OBJECTIVES

Fonte: `Bot Testing Ad Arte_v1.2.docx` (cliente: Leonardo, committente finale: Ad Arte).

## Obiettivo tecnico

Verificare l'effettiva attivazione delle protezioni antiBot configurate sul WAF FortiGate del tenant Ad Arte, limitatamente all'ambiente di **collaudo**.

La verifica avviene tramite 5 client BOT sviluppati ad hoc, che simulano altrettante categorie di azione malevola contro endpoint applicativi noti.

## Successo del test

Il successo consiste nel **rilevamento e blocco dei BOT da parte del WAF entro tempi misurabili**. L'eventuale assenza di blocco costituisce evidenza utile alla revisione delle policy antiBot.

Segnali osservabili lato client:
- Response HTTP 403, 429, 503
- Connection reset, timeout anomali
- Redirect a challenge page o pagina di errore generica
- Tempo trascorso e numero di richieste prima del primo blocco

Non è previsto accesso diretto a dashboard o log FortiGate lato test.

## Matrice BOT

| BOT | Categoria protezione | Bersaglio | Tipo client |
|---|---|---|---|
| BOT-1 | Denial of Service | Pagine di ricerca | HTTP async (httpx) |
| BOT-2 | Account Takeover | Login, Reset password | HTTP async (httpx) |
| BOT-3 | Creazione automatizzata account | Registrazione/Iscrizione | Browser (Playwright) |
| BOT-4 | Content Scraping | Pagine di navigazione | Browser (Playwright) |
| BOT-5 | Price Scraping | Catalogo prodotti | Browser (Playwright) |

Per il dettaglio endpoint per BOT vedere `08_endpoints.md`.

## Comportamento previsto

I BOT sono volutamente **palesi**: nessuna evasione. Il test misura la baseline di detection, non la resistenza del WAF ad attaccanti sofisticati. Dettaglio in `05_quirks.md` sezione "Vincoli comportamentali".

## Packaging

- Immagine Docker singola, parametrizzata via flag di lancio (`--bot <nome> --duration <durata>`).
- Distribuzione multi-VM Linode prevista dalla specifica ma **attualmente fuori scope** (decisione utente 2026-04-24: esecuzione locale).
- No Kubernetes.

## Pianificazione attività (da specifica, sez. 7)

| Giorno | Attività | Output atteso |
|---|---|---|
| 1 | Provisioning VM lab, repo Python, Dockerfile, logger, reporter, smoke test Playwright | Container deployabile |
| 2 | Sviluppo BOT-1 DoS | BOT-1 funzionante |
| 3 | Sviluppo BOT-2 ATO | BOT-2 funzionante |
| 4 | Sviluppo BOT-4 e BOT-5 scraping (codice condiviso) | BOT-4 e BOT-5 funzionanti |
| 5 | Sviluppo BOT-3 registration + distribuzione multi-VM + report consolidato | BOT-3 e report |
| Buffer | Iterazione su BOT che non hanno innescato detection, taratura parametri | Adeguamento parametri |

Adattamento locale del piano sarà documentato in changelog man mano.

## Out of scope (dalla specifica, sez. 8)

Non inclusi nel perimetro iniziale. Possono essere oggetto di fase successiva:

- Tecniche di evasione del WAF (stealth plugin Playwright, residential proxy, spoofing TLS fingerprint)
- Esecuzione dei test sull'ambiente di **produzione**
- Integrazione automatica con Datadog Synthetics
- Realizzazione di pipeline CI/CD per il deploy dei BOT
- Dashboard di monitoraggio in tempo reale
- Gestione massiva e rotazione di IP sorgente oltre alle VM Linode previste

## Deliverable finale

- Codice BOT versionato nel repo (5 BOT + codice comune + Docker)
- Report Markdown consolidato con:
  - Tabella di sintesi per categoria
  - Evidenze raccolte per ogni BOT (JSON -> Markdown)
  - Conclusioni operative
  - Allegato: export log FortiGate forniti dal SOC per le finestre di esecuzione
