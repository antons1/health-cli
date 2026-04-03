import json
import time
from pathlib import Path

CACHE_DIR = Path("~/.health-data/garmin/cache").expanduser()

STATIC_TTL = 4 * 3600    # 4 hours — sleep, HRV, RHR (finalized after wake-up)
DYNAMIC_TTL = 15 * 60    # 15 minutes — stress, body battery (update throughout the day)


def _cache_path(endpoint: str, date: str) -> Path:
    return CACHE_DIR / f"{endpoint}_{date}.json"


def read_cache(endpoint: str, date: str, ttl: int | None) -> dict | None:
    """Return cached data if valid, else None.

    ttl=None means no expiry (used for past dates where data is immutable).
    """
    path = _cache_path(endpoint, date)
    if not path.exists():
        return None
    entry = json.loads(path.read_text())
    if ttl is not None and time.time() - entry["cached_at"] > ttl:
        return None
    return entry["data"]


def write_cache(endpoint: str, date: str, data) -> None:
    """Write data to the cache with the current timestamp."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _cache_path(endpoint, date).write_text(
        json.dumps({"cached_at": time.time(), "data": data})
    )
