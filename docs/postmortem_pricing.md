# Postmortem: Incorrect Product Pricing Due to Cache Key Collision

## Summary

A simulated pricing incident caused product detail requests to return incorrect pricing data from Redis. The issue occurred because multiple product lookups shared the same cache key, allowing one product's cached payload to overwrite another's.

## Impact

Users requesting one product could receive the name and price of a different product. This is a high-severity ecommerce issue because it creates inconsistent product displays and could lead to incorrect checkout expectations.

## Detection

The issue was detectable through:

- inconsistent product responses across repeated requests
- structured logs showing repeated use of the same cache key for different product IDs
- cache hit logs that did not match the requested product ID

## Root Cause

The cache key strategy was incorrect. Instead of namespacing entries by product ID, the incident path intentionally used a shared Redis key:

`product:shared`

This created collisions between otherwise unrelated product records.

## Resolution

The fix is to use product-specific cache keys such as:

`product:{product_id}`

and verify through tests that distinct products never share cached payloads.

## Preventive Actions

- add automated tests for cache key isolation
- add assertions comparing requested product ID with returned product ID
- include log-based alerting for unexpected cache key reuse
- review cache design whenever response payloads contain identifiers and prices 

## Timeline

- T0 — Product detail endpoint deployed with Redis caching
- T0 + X — First request cached a product under the shared key `product:shared`
- T0 + X+1 — Subsequent product requests returned cached data from the shared key
- T0 + X+N — Engineers observed inconsistent product responses during testing
- T0 + X+N+1 — Root cause identified as incorrect cache key strategy
- T0 + X+N+2 — Fix proposed: use `product:{product_id}` cache key

## Reproduction Steps

1. Enable the incident flag in `infra/docker-compose.yml`:

```
INCIDENT_PRICING_CACHE=true
```

2. Start the system:

```
docker compose -f infra/docker-compose.yml up --build
```

3. Request the product list:

```
curl.exe "http://localhost:8080/products"
```

4. Request the first product:

```
curl.exe "http://localhost:8080/products/{product_id_1}"
```

5. Request a different product:

```
curl.exe "http://localhost:8080/products/{product_id_2}"
```

6. Observe the response.

Due to the cache key collision (`product:shared`), the second request may return the cached payload of the first product instead of its own product data.

Example behavior:

```
GET /products/{product_id_1}
→ Hoodie (cached under product:shared)

GET /products/{product_id_2}
→ Hoodie (incorrectly returned from cache)
```

This demonstrates how an incorrect Redis cache key design can cause cross-product data contamination in production systems.