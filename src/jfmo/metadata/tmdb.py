import requests
from loguru import logger


class TMDBClient:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key
        self._cache: dict[str, tuple[int | None, str | None]] = {}

        if not self.api_key:
            logger.warning("TMDB API key not configured. TMDB integration disabled.")
        else:
            self._validate_api_key()

    def _validate_api_key(self) -> None:
        result = self._make_request("authentication")
        if result and result.get("success"):
            logger.info("TMDB API key validated successfully.")
        else:
            logger.error("TMDB API key is invalid. TMDB integration disabled.")
            self.api_key = None

    def _cache_get(self, title: str, year: str | None) -> tuple[int | None, str | None] | None:
        return self._cache.get(f"{title}_{year or ''}")

    def _cache_set(self, title: str, year: str | None, tmdb_id: int | None, result_year: str | None) -> None:
        self._cache[f"{title}_{year or ''}"] = (tmdb_id, result_year)

    def _make_request(self, endpoint: str, params: dict | None = None) -> dict | None:
        if not self.api_key:
            return None

        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json;charset=utf-8",
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDB API request failed: {e}")
            return None

    def _pick_best(
        self, candidates: list[dict], title: str, year: str | None, date_key: str, title_key: str
    ) -> dict | None:
        if year:
            exact_year = [c for c in candidates if c.get(date_key, "").startswith(year)]
            if exact_year:
                candidates = exact_year

        title_lower = title.lower()
        exact_title = [c for c in candidates if c.get(title_key, "").lower() == title_lower]
        if exact_title:
            candidates = exact_title

        candidates.sort(key=lambda x: x.get("popularity", 0), reverse=True)
        return candidates[0] if candidates else None

    def _resolve(
        self, endpoint: str, title: str, year: str | None, date_key: str, title_key: str
    ) -> tuple[int | None, str | None]:
        cached = self._cache_get(title, year)
        if cached is not None:
            return cached

        if not self.api_key:
            return None, year

        params: dict = {"query": title, "include_adult": "false", "language": "en-US", "page": 1}
        if year:
            params["year"] = year

        data = self._make_request(endpoint, params)
        candidates = (data or {}).get("results") or []

        result = self._pick_best(candidates, title, year, date_key, title_key)
        if result:
            tmdb_id = result.get("id")
            date = result.get(date_key, "")
            result_year = date[:4] if date else year
            logger.info(f"TMDB match '{title}': ID {tmdb_id}, year {result_year}")
            self._cache_set(title, year, tmdb_id, result_year)
            return tmdb_id, result_year

        logger.warning(f"No TMDB match for '{title}' {year or ''}")
        self._cache_set(title, year, None, year)
        return None, year

    def search_movie(self, title: str, year: str | None = None) -> tuple[int | None, str | None]:
        return self._resolve("search/movie", title, year, "release_date", "title")

    def search_tv(self, title: str, year: str | None = None) -> tuple[int | None, str | None]:
        return self._resolve("search/tv", title, year, "first_air_date", "name")
