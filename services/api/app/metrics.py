from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

# Metrics counters used in checkout and incident handling paths.
# They make it easy to tell when injected failure scenarios are active.
CHECKOUT_FAILURES_TOTAL = Counter(
    "checkout_failures_total",
    "Total checkout failures",
)

CHECKOUT_REQUESTS_TOTAL = Counter(
    "checkout_requests_total",
    "Total checkout requests",
)


def metrics_response() -> Response:
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )