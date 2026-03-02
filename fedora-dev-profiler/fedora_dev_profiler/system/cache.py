"""
Handles deterministic session-level caching for the Fedora Dev Profiler.
Ensures repeated views and re-renders do not cause UI flicker or varying heuristics.
"""
from typing import Optional, Any

class SessionCache:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionCache, cls).__new__(cls)
            cls._instance.clear()
        return cls._instance

    def clear(self):
        """Clears all cached session data."""
        self._cache = {}
        
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value by key."""
        return self._cache.get(key)
        
    def set(self, key: str, value: Any):
        """Set a value in the session cache."""
        self._cache[key] = value

    def has(self, key: str) -> bool:
        """Check if cache contains key."""
        return key in self._cache

# Global singleton instance
cache = SessionCache()
