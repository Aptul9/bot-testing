# INFRASTRUCTURE

## Ambiente di test

Target unico per questa iniziativa: **ambiente di collaudo** Ad Arte. La produzione e' esplicitamente fuori scope.

| Elemento | Valore |
|---|---|
| Base URL API collaudo | `https://api-coll.museiitaliani.it` |
| Base URL API produzione (riferimento, non usare) | `https://api.museiitaliani.it` |
| WAF | Fortinet FortiGate (tenant Ad Arte) |
| Regione di provisioning client BOT | Fuori perimetro PSN (richiesto per far transitare il traffico dal WAF) |

## Microservizi backend

| Servizio | Tech | Path base collaudo | Swagger |
|---|---|---|---|
| cms-ms | Django/DRF | `/cms-ms/api` | `https://api-coll.museiitaliani.it/cms-ms/api/schema/swagger-ui/` |
| integration-app-web | Spring Boot | `/smnadarte-integration-app-web/app/api` | `https://api-coll.museiitaliani.it/smnadarte-integration-app-web/swagger-ui/index.html` |
| ssot-api | Spring Boot | `/collaudo/ssot/api` | `https://api-coll.museiitaliani.it/collaudo/ssot/api/swagger-ui/index.html` |
| ssot-event-generator | Spring Boot | `/collaudo/ssot/event` | `https://api-coll.museiitaliani.it/collaudo/ssot/event/swagger-ui/index.html` |
| ssot-pseudonymization | Spring Boot | `/collaudo/ssot/pseudonymization` | `https://api-coll.museiitaliani.it/collaudo/ssot/pseudonymization/swagger-ui/index.html` |
| aimusei-be | Spring Boot | `/aimusei/api` | `https://api-coll.museiitaliani.it/aimusei/api/swagger-ui/index.html` |

OpenAPI JSON disponibile su:
- `https://api-coll.museiitaliani.it/cms-ms/api/schema/`
- `https://api-coll.museiitaliani.it/smnadarte-integration-app-web/v3/api-docs`
- `https://api-coll.museiitaliani.it/aimusei/api/v3/api-docs`

## Identity provider

- **Keycloak** realm `AD-Arte-visitors` (owner backend Almaviva)
- Endpoint token: `POST /realms/AD-Arte-visitors/protocol/openid-connect/token`
- Endpoint admin users: `POST /admin/realms/AD-Arte-visitors/users`

Per elenco completo endpoint applicativi target vedere `08_endpoints.md`.

## Architettura del test

```
[BOT client (Python 3.12 in Docker)]
        |
        | HTTPS
        v
[WAF Fortinet FortiGate]
        |
        v
[Microservizi backend Ad Arte collaudo]
```

- I BOT girano **in locale** (decisione utente 2026-04-24), non su VM Linode.
- Il traffico deve transitare attraverso il WAF, altrimenti il test non e' valido.
- Non e' previsto accesso a dashboard FortiGate o log diretti del WAF lato test: misurazione basata solo su segnali client-side (codici HTTP, reset, timeout, challenge page).
- Log FortiGate richiesti al SOC **a test concluso**, come riscontro indipendente.

## Fuori scope infrastruttura

- Kubernetes / LKE
- NodeBalancer, Object Storage
- Container registry esterno (build Docker in locale)
- CI/CD pipeline
