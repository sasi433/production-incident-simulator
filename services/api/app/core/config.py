import os


def _env_flag(name: str, default: str = "false") -> bool:
    """
    Helper to read boolean feature flags from environment variables.
    """
    return os.getenv(name, default).strip().lower() == "true"


def incident_checkout_enabled() -> bool:
    """
    Enables the intermittent checkout failure scenario.
    """
    return _env_flag("INCIDENT_CHECKOUT")


def incident_pricing_cache_enabled() -> bool:
    """
    Enables the pricing cache bug scenario where multiple products
    share the same Redis cache key.
    """
    return _env_flag("INCIDENT_PRICING_CACHE")


def incident_session_reset_enabled() -> bool:
    """
    Enables the cart/session reset bug scenario where cart reads
    sometimes look up the wrong Redis key namespace.
    """
    return _env_flag("INCIDENT_SESSION_RESET")