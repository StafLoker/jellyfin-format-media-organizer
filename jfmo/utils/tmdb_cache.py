"""
Shared TMDB cache to avoid duplicate API calls
"""
from typing import Optional, Tuple, Dict


class TMDBCache:
    """Singleton cache for TMDB results"""
    
    _instance = None
    _cache: Dict[str, Tuple[Optional[int], Optional[str]]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TMDBCache, cls).__new__(cls)
        return cls._instance
    
    def get(self, title: str, year: Optional[str] = None) -> Optional[Tuple[Optional[int], Optional[str]]]:
        """
        Get cached TMDB result
        
        Args:
            title: Media title
            year: Release/air year
            
        Returns:
            Tuple of (tmdb_id, year) or None if not cached
        """
        cache_key = f"{title}_{year if year else ''}"
        return self._cache.get(cache_key)
    
    def set(self, title: str, year: Optional[str], tmdb_id: Optional[int], result_year: Optional[str]) -> None:
        """
        Store TMDB result in cache
        
        Args:
            title: Media title
            year: Release/air year used in search
            tmdb_id: TMDB ID found
            result_year: Year from TMDB result
        """
        cache_key = f"{title}_{year if year else ''}"
        self._cache[cache_key] = (tmdb_id, result_year)
    
    def clear(self) -> None:
        """Clear all cached results"""
        self._cache.clear()