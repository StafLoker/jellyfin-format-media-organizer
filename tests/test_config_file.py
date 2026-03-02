import pytest
import yaml

from jfmo.config import config


def write_yaml(path, data):
    with open(path, "w") as f:
        yaml.dump(data, f)


def _make_dirs(tmp_path):
    """Create temp directories to satisfy validation."""
    d = tmp_path / "downloads"
    f = tmp_path / "films"
    t = tmp_path / "tv"
    d.mkdir()
    f.mkdir()
    t.mkdir()
    return str(d), str(f), str(t)


def _base_data(tmp_path):
    """Return minimal valid config data with real directories."""
    dl, fl, tv = _make_dirs(tmp_path)
    return {
        "directories": {
            "downloads": {"path": dl},
            "media": {"films": fl, "tv": tv},
        },
        "daemon": {"interval": 60},
    }


# ---------------------------------------------------------------------------
# load — missing / invalid file
# ---------------------------------------------------------------------------


def test_load_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        config.load(str(tmp_path / "missing.yaml"))


def test_load_invalid_yaml(tmp_path):
    cfg = tmp_path / "bad.yaml"
    cfg.write_text("key: [unclosed")
    with pytest.raises(ValueError, match="Invalid YAML"):
        config.load(str(cfg))


# ---------------------------------------------------------------------------
# load — directories
# ---------------------------------------------------------------------------


def test_load_directories(tmp_path):
    data = _base_data(tmp_path)
    cfg = tmp_path / "config.yaml"
    write_yaml(cfg, data)
    config.load(str(cfg))

    dl = data["directories"]["downloads"]["path"]
    fl = data["directories"]["media"]["films"]
    tv = data["directories"]["media"]["tv"]
    assert dl == config.DOWNLOADS_DIR
    assert fl == config.FILMS_DIR
    assert tv == config.TV_DIR


# ---------------------------------------------------------------------------
# load — TMDB
# ---------------------------------------------------------------------------


def test_load_tmdb_api_key(tmp_path):
    data = _base_data(tmp_path)
    data["tmdb"] = {"api_key": "abc123"}
    cfg = tmp_path / "config.yaml"
    write_yaml(cfg, data)
    config.load(str(cfg))
    assert config.TMDB_API_KEY == "abc123"


def test_load_tmdb_empty_key_not_overwritten(tmp_path):
    """Empty api_key in YAML should not overwrite existing key."""
    data = _base_data(tmp_path)
    data["tmdb"] = {"api_key": ""}
    cfg = tmp_path / "config.yaml"
    write_yaml(cfg, data)
    config.TMDB_API_KEY = "existing"
    config.load(str(cfg))
    assert config.TMDB_API_KEY == "existing"


# ---------------------------------------------------------------------------
# load — logging
# ---------------------------------------------------------------------------


def test_load_logging(tmp_path):
    data = _base_data(tmp_path)
    data["logging"] = {"log_level": "debug"}
    cfg = tmp_path / "config.yaml"
    write_yaml(cfg, data)
    config.load(str(cfg))
    assert config.LOG_LEVEL == "DEBUG"


# ---------------------------------------------------------------------------
# load — naming tokens
# ---------------------------------------------------------------------------


def test_load_naming_tokens(tmp_path):
    data = _base_data(tmp_path)
    data["naming"] = {
        "movies": {"file": "{title} ({year})"},
        "tv": {
            "folder": "{title} ({year})",
            "season": "Season {season}",
            "file": "{title} S{season}E{episode}",
        },
    }
    cfg = tmp_path / "config.yaml"
    write_yaml(cfg, data)
    config.load(str(cfg))
    assert config.FORMAT_MOVIE_FILE == "{title} ({year})"
    assert config.FORMAT_TV_FOLDER == "{title} ({year})"
    assert config.FORMAT_TV_SEASON_FOLDER == "Season {season}"
    assert config.FORMAT_TV_FILE == "{title} S{season}E{episode}"


def test_load_naming_invalid_token_in_movie(tmp_path):
    """episode token is not valid in movie file pattern."""
    data = _base_data(tmp_path)
    data["naming"] = {"movies": {"file": "{title} {episode}"}}
    cfg = tmp_path / "config.yaml"
    write_yaml(cfg, data)
    with pytest.raises(ValueError, match="naming.movies.file"):
        config.load(str(cfg))


def test_load_naming_invalid_token_in_tv_season(tmp_path):
    """episode token is not valid in season folder pattern."""
    data = _base_data(tmp_path)
    data["naming"] = {"tv": {"season": "Season {season} {episode}"}}
    cfg = tmp_path / "config.yaml"
    write_yaml(cfg, data)
    with pytest.raises(ValueError, match="naming.tv.season"):
        config.load(str(cfg))


def test_load_naming_invalid_token_in_tv_folder(tmp_path):
    """episode/season tokens are not valid in TV folder pattern."""
    data = _base_data(tmp_path)
    data["naming"] = {"tv": {"folder": "{title} S{season}E{episode}"}}
    cfg = tmp_path / "config.yaml"
    write_yaml(cfg, data)
    with pytest.raises(ValueError, match="naming.tv.folder"):
        config.load(str(cfg))


# ---------------------------------------------------------------------------
# load — daemon
# ---------------------------------------------------------------------------


def test_load_daemon_interval(tmp_path):
    data = _base_data(tmp_path)
    data["daemon"]["interval"] = 120
    cfg = tmp_path / "config.yaml"
    write_yaml(cfg, data)
    config.load(str(cfg))
    assert config.DAEMON_INTERVAL_SEC == 120


def test_load_daemon_interval_too_low(tmp_path):
    """Interval <= 30 should raise ValueError."""
    data = _base_data(tmp_path)
    data["daemon"]["interval"] = 10
    cfg = tmp_path / "config.yaml"
    write_yaml(cfg, data)
    with pytest.raises(ValueError, match="daemon.interval must be >= 30"):
        config.load(str(cfg))


# ---------------------------------------------------------------------------
# validation — missing directories
# ---------------------------------------------------------------------------


def test_validate_missing_directories(tmp_path):
    """Config with non-existent directories should raise ValueError."""
    data = {
        "directories": {
            "downloads": {"path": "/nonexistent/downloads"},
            "media": {"films": "/nonexistent/films", "tv": "/nonexistent/tv"},
        },
        "daemon": {"interval": 60},
    }
    cfg = tmp_path / "config.yaml"
    write_yaml(cfg, data)
    with pytest.raises(ValueError, match="Directory does not exist"):
        config.load(str(cfg))
