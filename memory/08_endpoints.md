# ENDPOINTS

Fonte: `URL-WAF AntiBoT.xlsx`, `API_antiBot_AdArte.xlsx`.

Base URL collaudo: `https://api-coll.museiitaliani.it`

Nota: in produzione il path `/smnadarte-integration-app-web/app/api` corrisponde. Per il test va usato **solo** collaudo.

## Endpoint integration-app-web (prefisso `/smnadarte-integration-app-web/app/api`)

| Endpoint | Funzione | Categoria WAF | BOT associato |
|---|---|---|---|
| `POST /login` | Login | Account Takeover | BOT-2 |
| `GET /account/user` | Dati utente post-login | Account Takeover | BOT-2 |
| `GET /offer/availability` | Disponibilita' offerte | Price Scraping | BOT-5 |
| `GET /zone/codesr/{codesr}` | Zona per codice SR | Price Scraping | BOT-5 |
| `GET /zone/{idezon}` | Zona per id | Price Scraping | BOT-5 |
| `GET /offer/timeslot` | Slot temporali offerte | Price Scraping | BOT-5 |
| `GET /reservation/access/{qr}` | Info accesso prenotazione | Content Scraping | BOT-4 |
| `GET /reservation/for/{qr}` | Dettaglio prenotazione | Content Scraping | BOT-4 |
| `GET /reservation/zone/{qr}` | Zona prenotazione | Content Scraping | BOT-4 |
| `POST /guest/prepareorder` | Prepara ordine guest | Price Scraping | BOT-5 |
| `POST /prepareorder` | Prepara ordine | Price Scraping | BOT-5 |
| `POST /group/reservation/summary` | Riepilogo prenotazione gruppo | Price Scraping | BOT-5 |
| `POST /group/reservation/payment` | Pagamento prenotazione gruppo | Price Scraping | BOT-5 |
| `POST /group/reservation/private/find/details` | Dettagli prenotazione privata | Price Scraping | BOT-5 |

## Endpoint Keycloak (realm `AD-Arte-visitors`, owner Almaviva)

| Endpoint | Funzione | BOT associato |
|---|---|---|
| `POST /realms/AD-Arte-visitors/protocol/openid-connect/token` | Login via OIDC | BOT-2 (ATO) |
| `POST /admin/realms/AD-Arte-visitors/users` | Creazione utente (admin) | BOT-3 (registration) |

`POST /admin/realms/.../users` richiede admin token Keycloak. Verificare in fase di implementazione BOT-3 se esiste un endpoint self-registration esposto al visitor che non richieda admin bearer.

## Endpoint ticketing (componente ticketing, owner Almaviva)

Dallo sheet `API` del file `API_antiBot_AdArte.xlsx`, caso d'uso "utente che acquista un biglietto gratuito":

- `GET /app/zone/codesr`
- `GET /app/offer/availability`
- `GET /app/offer/timeslot`
- `POST /app/prepareOrder`

Da verificare se il prefisso completo in collaudo e' `/smnadarte-integration-app-web/app/...` (coincide con integration-app-web) oppure un servizio distinto.

## Endpoint NON forniti (gap)

**BOT-1 Denial of Service**: la specifica parla di "pagine di ricerca" come bersaglio ma gli Excel NON contengono un endpoint di search. Possibili candidati da verificare con il cliente o da swagger:

- cms-ms `/cms-ms/api/public/cached/museum/` (endpoint cached monitorato da Datadog)
- cms-ms `/cms-ms/api/public/cached/museum-with-e-ticketing`
- cms-ms `/cms-ms/api/public/cached/museum/{id}`
- cms-ms `/cms-ms/api/public/cached/overview`

Conferma necessaria prima di eseguire BOT-1.

## Categorie di protezione WAF (da sheet `Categoria di protezione`)

| Categoria | Descrizione | Bersaglio tipico |
|---|---|---|
| Denial of Service (DoS) | Sovraccarico di traffico | Pagine di ricerca |
| Acquisizione dell'account (ATO) | Accessi non autorizzati | Login, Reset password |
| Creazione automatizzata account | Bot che creano profili falsi | Registrazione/Iscrizione |
| Content Scraping | Estrazione contenuti, articoli, immagini | Pagine di navigazione |
| Price Scraping | Raccolta prezzi automatizzata | Pagine di navigazione / Catalogo prodotti |
