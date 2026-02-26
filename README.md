# production-incident-simulator

A dockerized mini production system that will simulate real production incidents with observability and postmortems.

> Day 1: System foundation only (no incidents yet)

---

## What Exists Today

The system boots with:

- FastAPI (API service)
- PostgreSQL (database container)
- Redis (cache/session container)
- Nginx (reverse proxy)
- Docker Compose (orchestration)

No business logic or failure simulations yet.  
This commit establishes the production-style infrastructure layout.

---

## Architecture (Day 1)

Client → Nginx → FastAPI

PostgreSQL and Redis containers are running but not yet wired into the API.

---

## Run Locally

From project root:

```bash
docker compose -f infra/docker-compose.yml up --build
```

Open:

```
http://localhost:8080/healthz
```

Expected response:

```json
{"status":"ok"}
```

---

## Project Structure (Current)

```
production-incident-simulator/
  services/
    api/
    nginx/
  infra/
    docker-compose.yml
  README.md
```

---

## Upcoming Work

- Structured JSON logging
- Correlation IDs
- Readiness checks (/readyz)
- PostgreSQL integration
- Redis sessions
- Intentional incident simulations
- Runbook and postmortems

---

## Purpose of This Project

This repository is designed to demonstrate:

- Production-oriented system design
- Debugging maturity
- Observability-first thinking
- Real-world failure analysis

More features and incident simulations will be added in upcoming commits.