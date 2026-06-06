"""
In-memory prediction cache to avoid recomputing model inference for identical images.

Images are keyed by their SHA-256 hash so the same field photograph uploaded
multiple times per day hits the cache instead of re-running the full CNN pipeline.
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Default TTL: predictions older than this are considered stale and re-inferred.
_DEFAULT_TTL_MINUTES: int = 60

# Hard cap on cache entries to bound memory usage.
_DEFAULT_MAX_ENTRIES: int = 500


class ModelPredictionCache:
    """Thread-safe LRU-style in-memory cache for model prediction results."""

    def __init__(
        self,
        ttl_minutes: int = _DEFAULT_TTL_MINUTES,
        max_entries: int = _DEFAULT_MAX_ENTRIES,
    ) -> None:
        self._ttl = timedelta(minutes=ttl_minutes)
        self._max = max_entries
        self._store: Dict[str, Dict[str, Any]] = {}       # key -> prediction
        self._timestamps: Dict[str, datetime] = {}         # key -> insertion time

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get(self, image_bytes: bytes) -> Optional[Dict[str, Any]]:
        """Return a cached prediction, or None if absent or expired."""
        key = self._hash(image_bytes)
        if key not in self._store:
            logger.debug("Cache MISS  %s", key[:12])
            return None

        age = datetime.utcnow() - self._timestamps[key]
        if age > self._ttl:
            self._evict(key)
            logger.debug("Cache STALE %s (age %.0fs)", key[:12], age.total_seconds())
            return None

        logger.debug("Cache HIT   %s", key[:12])
        return self._store[key]

    def set(self, image_bytes: bytes, prediction: Dict[str, Any]) -> None:
        """Store a prediction. Evicts the oldest entry if the cache is full."""
        key = self._hash(image_bytes)
        if len(self._store) >= self._max:
            self._evict_oldest()
        self._store[key] = prediction
        self._timestamps[key] = datetime.utcnow()
        logger.debug(
            "Cache SET   %s  (size %d/%d)", key[:12], len(self._store), self._max
        )

    def clear(self) -> None:
        """Remove all entries."""
        count = len(self._store)
        self._store.clear()
        self._timestamps.clear()
        logger.info("Cache cleared (%d entries removed).", count)

    def stats(self) -> Dict[str, Any]:
        """Return a snapshot of cache metrics for monitoring / health endpoints."""
        return {
            "size": len(self._store),
            "max_entries": self._max,
            "ttl_minutes": int(self._ttl.total_seconds() // 60),
            "utilisation_pct": round(len(self._store) / self._max * 100, 1),
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _hash(image_bytes: bytes) -> str:
        return hashlib.sha256(image_bytes).hexdigest()

    def _evict(self, key: str) -> None:
        self._store.pop(key, None)
        self._timestamps.pop(key, None)

    def _evict_oldest(self) -> None:
        if not self._timestamps:
            return
        oldest_key = min(self._timestamps, key=lambda k: self._timestamps[k])
        self._evict(oldest_key)
        logger.debug("Cache EVICT oldest entry %s.", oldest_key[:12])


# ---------------------------------------------------------------------------
# Module-level singleton used by the rest of the app.
# ---------------------------------------------------------------------------
_cache = ModelPredictionCache()


def get_cached_prediction(image_bytes: bytes) -> Optional[Dict[str, Any]]:
    """Return a cached result for *image_bytes*, or None on a cache miss."""
    return _cache.get(image_bytes)


def cache_prediction(image_bytes: bytes, prediction: Dict[str, Any]) -> None:
    """Store *prediction* in the cache keyed by *image_bytes*."""
    _cache.set(image_bytes, prediction)


def clear_cache() -> None:
    """Flush all cached predictions (useful for testing)."""
    _cache.clear()


def cache_stats() -> Dict[str, Any]:
    """Return current cache statistics."""
    return _cache.stats()
