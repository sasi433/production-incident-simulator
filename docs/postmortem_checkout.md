# Postmortem: Checkout Intermittent Failure

## Summary

Checkout intermittently failed for a subset of users due to an intentionally injected application fault used to simulate a production incident.

## Impact

- Affected endpoint: `POST /checkout`
- User impact: some checkout requests failed with HTTP 500
- Approximate failure rate: 25%
- Additional symptom: some requests were delayed by ~2 seconds

## Detection

The issue was detected through:

- structured application logs
- correlation IDs in request logs
- repeated checkout test requests showing intermittent failures

Example signal:
- `incident_checkout_failure_triggered`
- `incident_checkout_delay_triggered`

## Timeline

- Incident toggle enabled via `INCIDENT_CHECKOUT=true`
- Repeated checkout requests produced intermittent 500 responses
- Logs showed correlation IDs and incident trigger messages
- Incident mitigated by disabling the toggle

## Root Cause

The checkout route intentionally injected intermittent failures and delays when the `INCIDENT_CHECKOUT` environment variable was enabled.

This simulates real production failure patterns such as:

- transient dependency failures
- database lock/contention
- downstream timeout behavior

## Resolution

Set:

```env
INCIDENT_CHECKOUT=false
```

Then restart the service.

## Preventive Actions

- Add retry policy for safe/idempotent operations where appropriate
- Add alerting on elevated checkout failure rate
- Add latency SLO monitoring for checkout
- Introduce circuit breaking or fallback behavior for dependent services

## Lessons Learned

- Correlation IDs make intermittent incidents easier to trace
- Structured logs are essential for debugging non-deterministic failures
- Controlled failure injection is useful for validating observability and response procedures