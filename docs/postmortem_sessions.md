# Postmortem: Cart Randomly Reset Due to Redis Key Namespace Mismatch

## Summary

A simulated session/cart incident caused users to intermittently see an empty cart even after successfully adding items. The issue was caused by inconsistent Redis key usage between cart write and cart read paths.

## Timeline

- T0 — Cart persistence was deployed using Redis-backed session-scoped keys
- T0 + X — Users successfully added items to cart under the expected Redis key
- T0 + X+1 — Some cart reads began looking up a different Redis namespace
- T0 + X+N — Engineers observed that cart state appeared to disappear intermittently
- T0 + X+N+1 — Root cause identified as a key namespace mismatch between read and write paths
- T0 + X+N+2 — Fix proposed: standardize cart key generation in a single shared helper

## Impact

Users could add items to their cart and then later see an empty cart on refresh or subsequent reads. This would create a broken shopping experience and reduce checkout completion.

## Detection

The issue was detectable through:

- reports of carts appearing empty after items had been added
- logs showing successful cart writes but intermittent cart lookup misses
- Redis key inspection showing writes under `cart:{session_id}` while some reads queried `cart:v2:{session_id}`

## Root Cause

The write path stored cart state under the correct Redis key:

`cart:{session_id}`

However, the incident path caused the read logic to sometimes query a different namespace:

`cart:v2:{session_id}`

Because the read key did not match the write key, the application interpreted the missing Redis entry as an empty cart.

## Resolution

The fix is to ensure cart read and write paths use the same shared key builder and never diverge across namespaces unless explicitly versioned and migrated safely.

## Reproduction Steps

1. Enable the incident flag in `infra/docker-compose.yml`:

```
INCIDENT_SESSION_RESET=true
```

2. Start the system:

```
docker compose -f infra/docker-compose.yml up --build
```

3. Log in and store the `session_id` cookie returned in the response header.

4. Add an item to the cart:

```
POST /cart/items
```

5. Read the cart multiple times:

```
GET /cart
GET /cart
GET /cart
```

6. Observe that some requests return the expected cart contents while others return an empty cart because the application queried the wrong Redis key.

## Preventive Actions

- centralize Redis key generation for cart/session data
- add automated tests that verify read and write key consistency
- add alerts for repeated cart lookup misses following successful writes
- avoid partial namespace migrations without dual-read or migration support