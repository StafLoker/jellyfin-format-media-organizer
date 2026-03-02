import os
import re
import sys
from pathlib import Path

import yaml
from loguru import logger

# Valid tokens per naming pattern
_VALID_TOKENS: dict[str, set[str]] = {
    "naming.movies.file": {"title", "year", "quality", "tmdb_id"},
    "naming.tv.folder": {"title", "year", "tmdb_id"},
    "naming.tv.season": {"season"},
    "naming.tv.file": {"title", "season", "episode", "quality"},
}


class Config:
    def __init__(self) -> None:
        self.LOG_LEVEL: str = "INFO"

        self.DAEMON_INTERVAL_SEC: int = 30

        self.DOWNLOADS_DIR: str
        self.FILMS_DIR: str
        self.TV_DIR: str

        # Naming format tokens
        self.FORMAT_MOVIE_FILE: str = "{title} ({year}) [tmdbid-{tmdb_id}] - {quality}"
        self.FORMAT_TV_FOLDER: str = "{title} ({year}) [tmdbid-{tmdb_id}]"
        self.FORMAT_TV_SEASON_FOLDER: str = "Season {season}"
        self.FORMAT_TV_FILE: str = "{title} S{season}E{episode} - {quality}"

        # TMDB configuration
        self.TMDB_API_KEY: str | None = None

        self.DRY_RUN: bool = False
        self.DAEMON_MODE: bool = False

    def _setup_logger(self) -> None:
        logger.remove()

        logger.add(
            sys.stderr,
            colorize=True,
            level=self.LOG_LEVEL,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        )

        log_dir = Path("/var/log/jfmo")
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            logger.add(
                str(log_dir / ("jfmo_{time:YYYY-MM-DD}.log")),
                rotation="10 MB",
                retention="30 days",
                compression="zip",
                level=self.LOG_LEVEL,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            )
        except PermissionError:
            pass  # No file logging if lacking permissions

    def load(self, path: str) -> None:
        """Load configuration from a YAML file.

        Raises:
            FileNotFoundError: If the config file does not exist.
            ValueError: If the YAML is invalid or cannot be applied.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}") from e

        if not data:
            self._setup_logger()
            return

        # Logging
        if "logging" in data:
            log = data["logging"]
            if "log_level" in log:
                self.LOG_LEVEL = log["log_level"].upper()

        # Daemon
        if "daemon" in data and "interval" in data["daemon"]:
            self.DAEMON_INTERVAL_SEC = data["daemon"]["interval"]

        # Directories
        if "directories" in data:
            dirs = data["directories"]
            if "downloads" in dirs:
                dl = dirs["downloads"]
                if isinstance(dl, dict) and "path" in dl:
                    self.DOWNLOADS_DIR = dl["path"]
            if "media" in dirs:
                media = dirs["media"]
                if "films" in media:
                    self.FILMS_DIR = media["films"]
                if "tv" in media:
                    self.TV_DIR = media["tv"]

        # Naming tokens
        if "naming" in data:
            naming = data["naming"]
            if "movies" in naming and isinstance(naming["movies"], dict) and "file" in naming["movies"]:
                self.FORMAT_MOVIE_FILE = naming["movies"]["file"]
            if "tv" in naming and isinstance(naming["tv"], dict):
                tv = naming["tv"]
                if "folder" in tv:
                    self.FORMAT_TV_FOLDER = tv["folder"]
                if "season" in tv:
                    self.FORMAT_TV_SEASON_FOLDER = tv["season"]
                if "file" in tv:
                    self.FORMAT_TV_FILE = tv["file"]

        # TMDB
        if "tmdb" in data and (api_key := data["tmdb"].get("api_key")):
            self.TMDB_API_KEY = api_key

        self._setup_logger()
        self._validate()

    def _validate(self) -> None:
        """Validate configuration values after loading.

        Raises:
            ValueError: If required directories are missing or paths do not exist.
        """
        errors: list[str] = []

        # Required directory attributes must be set
        for attr in ("DOWNLOADS_DIR", "FILMS_DIR", "TV_DIR"):
            if not hasattr(self, attr):
                errors.append(f"Required directory not configured: '{attr.lower()}'")
            else:
                path = getattr(self, attr)
                if not os.path.exists(path):
                    errors.append(f"Directory does not exist: {attr}={path!r}")
                elif not os.path.isdir(path):
                    errors.append(f"Path is not a directory: {attr}={path!r}")

        if self.DAEMON_INTERVAL_SEC < 30:
            errors.append(f"daemon.interval must be >= 30, got {self.DAEMON_INTERVAL_SEC}")

        errors.extend(self._validate_naming_patterns())

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

    def _validate_naming_patterns(self) -> list[str]:
        errors = []
        token_pattern = re.compile(r"\{(\w+)\}")

        for label, pattern in [
            ("naming.movies.file", self.FORMAT_MOVIE_FILE),
            ("naming.tv.folder", self.FORMAT_TV_FOLDER),
            ("naming.tv.season", self.FORMAT_TV_SEASON_FOLDER),
            ("naming.tv.file", self.FORMAT_TV_FILE),
        ]:
            used_tokens = set(token_pattern.findall(pattern))
            unknown = used_tokens - _VALID_TOKENS[label]
            if unknown:
                errors.append(f"{label}: invalid tokens {unknown} (allowed: {_VALID_TOKENS[label]})")

        return errors

    def __str__(self) -> str:
        return (
            f"Current configuration:\n"
            f"  Download: {self.DOWNLOADS_DIR}\n"
            f"  Films: {self.FILMS_DIR} - TV: {self.TV_DIR}\n"
            f"  Daemon Interval: {self.DAEMON_INTERVAL_SEC} sec\n"
            f"  TMDB Integration: {'enable' if self.TMDB_API_KEY else 'disable'}"
        )


config = Config()
