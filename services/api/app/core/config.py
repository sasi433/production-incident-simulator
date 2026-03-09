import os


def incident_checkout_enabled() -> bool:
    return os.getenv("INCIDENT_CHECKOUT", "false").strip().lower() == "true"