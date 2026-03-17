# production-incident-simulator

A dockerized mini production system that simulates real-world production incidents with observability, metrics, and postmortems.

This project is designed to demonstrate **senior-level backend and production engineering skills** including debugging, system design, and incident analysis.

---

## What This Project Includes

A fully working production-style stack:

- FastAPI (application service)
- PostgreSQL (persistent storage)
- Redis (sessions + caching)
- Nginx (reverse proxy)
- Docker Compose (orchestration)

### Implemented Capabilities

- Structured JSON logging (structlog)
- Correlation ID tracing across requests
- Readiness and health endpoints
- Redis-backed sessions and cart
- Product caching layer
- Prometheus metrics (`/metrics`)
- Load testing script
- Incident runbook
- Postmortem documentation

---

## Simulated Production Incidents

This system intentionally includes **realistic failure scenarios** that can be toggled via environment variables.

### 1. Checkout Intermittent Failure

```
INCIDENT_CHECKOUT=true
```

- Random request failures (~25%)
- Artificial latency injection
- Demonstrates retry/debug scenarios

---

### 2. Pricing Cache Bug

```
INCIDENT_PRICING_CACHE=true
```

- Incorrect Redis cache key usage
- Product responses may return wrong pricing
- Demonstrates cache invalidation issues

---

### 3. Session / Cart Reset Bug

```
INCIDENT_SESSION_RESET=true
```

- Redis key mismatch for cart
- Cart appears to randomly reset
- Demonstrates session consistency problems

---

## Architecture

```
Client → Nginx → FastAPI
                 ↓
        ---------------------
        |   PostgreSQL      |
        |   Redis           |
        ---------------------
```

### Key Design Decisions

- Separation of concerns (API / infra / services)
- Redis used for both session state and caching
- Postgres used for durable order storage
- Observability added before scaling complexity

---

## Run Locally

From project root:

```bash
docker compose -f infra/docker-compose.yml up --build
```

---

## Endpoints

### Health

```
GET /healthz
```

### Readiness

```
GET /readyz
```

### Products

```
GET /products
GET /products/{id}
```

### Cart

```
GET /cart
POST /cart/items
```

### Checkout

```
POST /checkout
```

### Metrics

```
GET /metrics
```

---

## Example Usage

### Login

```bash
curl.exe -X POST http://localhost:8080/login
```

### Add to cart

```bash
curl.exe -X POST \
  --cookie "session_id=YOUR_SESSION_ID" \
  -H "Content-Type: application/json" \
  --data-binary "@body.json" \
  http://localhost:8080/cart/items
```

### Checkout

```bash
curl.exe -X POST \
  -H "Content-Type: application/json" \
  --data-binary "@checkout_body.json" \
  http://localhost:8080/checkout
```

---

## Observability

### Metrics

Available at:

```
http://localhost:8080/metrics
```

Includes:

- `http_requests_total`
- `http_request_duration_seconds`
- `checkout_requests_total`
- `checkout_failures_total`

---

### Logs

Structured JSON logs include:

- correlation IDs
- request metadata
- incident triggers
- cache hits/misses
- session lookup issues

---

## Load Testing

Basic load test script:

```
scripts/load_test.sh
```

Example:

```bash
BASE_URL=http://localhost:8080 REQUESTS=50 ./scripts/load_test.sh
```

Use this to:

- trigger checkout failures
- observe latency spikes
- inspect metrics behavior

---

## Runbook

See:

```
docs/runbook.md
```

Includes:

- how to reproduce each incident
- what logs to inspect
- what metrics to monitor

---

## Postmortems

Each incident includes a postmortem:

- `postmortem_checkout.md`
- `postmortem_pricing.md`
- `postmortem_sessions.md`

These document:

- impact
- root cause
- detection
- resolution
- prevention strategies

---

## How I Would Improve This in Production

- Add distributed tracing (OpenTelemetry)
- Introduce circuit breakers and retries
- Add cache invalidation strategies
- Implement background workers (Celery / Kafka)
- Add alerting based on Prometheus metrics
- Introduce CI/CD pipeline with automated tests
- Add chaos engineering scenarios

---

## Project Structure

```
production-incident-simulator/
  services/
    api/
      app/
        routers/
        services/
        core/
        clients/
    nginx/
  infra/
    docker-compose.yml
  docs/
    runbook.md
    postmortems/
  scripts/
    load_test.sh
  README.md
```

---

## Purpose of This Project

This project demonstrates:

- production debugging mindset
- system observability design
- realistic failure modeling
- ability to reason about distributed systems
- backend engineering maturity beyond CRUD APIs

---

