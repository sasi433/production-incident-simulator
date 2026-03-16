# Incident Runbook

## Overview

This project simulates several common production incidents in a small ecommerce-style backend stack using FastAPI, Redis, Postgres, and Nginx.

The system exposes structured logs, readiness checks, and Prometheus metrics to support incident reproduction and debugging.

## Available Incident Flags

Set these in `infra/docker-compose.yml` under the API service environment.

### Checkout incident

```
INCIDENT_CHECKOUT=true
```

Effect:
- intermittent checkout failures
- delayed checkout responses

### Pricing cache incident

```
INCIDENT_PRICING_CACHE=true
```

Effect:
- multiple product requests may share the same Redis cache key
- incorrect product data may be returned

### Session/cart reset incident

```
INCIDENT_SESSION_RESET=true
```

Effect:
- cart reads may query the wrong Redis key namespace
- cart appears to reset intermittently

## Basic Validation

Start the system:

```
docker compose -f infra/docker-compose.yml up --build
```

Health check:

```
curl.exe "http://localhost:8080/healthz"
```

Readiness check:

```
curl.exe "http://localhost:8080/readyz"
```

Metrics:

```
curl.exe "http://localhost:8080/metrics"
```

## Reproducing Incident 1: Checkout Failure

1. Set:

```
INCIDENT_CHECKOUT=true
```

2. Rebuild and start the stack.

3. Run repeated checkout requests:

```
curl.exe -X POST "http://localhost:8080/checkout"
```

Or use the load test script:

```
BASE_URL=http://localhost:8080 REQUESTS=20 ./scripts/load_test.sh
```

4. Observe:
- intermittent HTTP 500 responses
- increased checkout failure counter in `/metrics`
- structured error logs in API logs

## Reproducing Incident 2: Pricing Cache Bug

1. Set:

```
INCIDENT_PRICING_CACHE=true
```

2. Rebuild and start the stack.

3. Fetch products:

```
curl.exe "http://localhost:8080/products"
```

4. Request two different product IDs in sequence.

5. Observe:
- second request may return cached data from the first product
- API logs show shared cache key usage

## Reproducing Incident 3: Session Reset Bug

1. Set:

```
INCIDENT_SESSION_RESET=true
```

2. Rebuild and start the stack.

3. Log in, add an item to the cart, and read `/cart` multiple times.

4. Observe:
- some requests return the expected cart
- some requests return `{"items":[]}`
- API logs show cart key namespace mismatch

## Metrics to Inspect

Key Prometheus metrics exposed at `/metrics`:

- `http_requests_total`
- `http_request_duration_seconds`
- `checkout_requests_total`
- `checkout_failures_total`

## Logs

Inspect API logs:

```
docker compose -f infra/docker-compose.yml logs api --tail 200
```

Inspect Nginx logs:

```
docker compose -f infra/docker-compose.yml logs nginx --tail 100
```