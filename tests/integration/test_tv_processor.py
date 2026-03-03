from pathlib import Path
from unittest.mock import MagicMock

import pytest

from jfmo.config import config
from jfmo.metadata.tmdb import TMDBClient
from jfmo.parser.context import MediaType, ParseContext
from jfmo.processors.tv_processor import TvProcessor


@pytest.fixture
def tv_dir(tmp_path):
    d = tmp_path / "tv"
    d.mkdir()
    config.TV_DIR = str(d)
    config.DRY_RUN = False
    config.FORMAT_TV_FOLDER = "{title} ({year}) [tmdbid-{tmdb_id}]"
    config.FORMAT_TV_SEASON_FOLDER = "Season {season}"
    config.FORMAT_TV_FILE = "{title} S{season}E{episode} - {quality}"
    return d


@pytest.fixture
def source_file(tmp_path):
    def _make(filename: str) -> Path:
        src = tmp_path / "downloads" / filename
        src.parent.mkdir(exist_ok=True)
        src.write_bytes(b"\x00" * 1024)
        return src

    return _make


@pytest.fixture
def mock_tmdb():
    tmdb = MagicMock(spec=TMDBClient)
    tmdb.search_tv.return_value = (1396, "2008")
    return tmdb


def _ctx(filepath: str, **tokens) -> ParseContext:
    return ParseContext(
        filepath=filepath,
        extension=Path(filepath).suffix,
        media_type=MediaType.TV,
        tokens=dict(tokens),
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_full_metadata(tv_dir, source_file, mock_tmdb):
    src = source_file("Breaking.Bad.S01E05.1080p.mkv")
    ctx = _ctx(str(src), title="Breaking Bad", year="2008", season="01", episode="05", quality="[1080p]")

    result = TvProcessor(mock_tmdb).process(ctx)

    assert result.success is True
    dest = tv_dir / "Breaking Bad (2008) [tmdbid-1396]" / "Season 01" / "Breaking Bad S01E05 - [1080p].mkv"
    assert dest.exists()
    assert dest.stat().st_ino == src.stat().st_ino  # hard link


def test_nested_dirs_auto_created(tv_dir, source_file, mock_tmdb):
    """Season and show directories are created automatically."""
    src = source_file("Show.S02E03.mkv")
    ctx = _ctx(str(src), title="Show", season="02", episode="03")

    TvProcessor(mock_tmdb).process(ctx)

    season_dir = tv_dir / "Show (2008) [tmdbid-1396]" / "Season 02"
    assert season_dir.is_dir()


def test_tmdb_provides_year(tv_dir, source_file, mock_tmdb):
    """Year comes from TMDB when absent from filename."""
    mock_tmdb.search_tv.return_value = (1396, "2008")
    src = source_file("Breaking.Bad.S01E01.mkv")
    ctx = _ctx(str(src), title="Breaking Bad", season="01", episode="01")

    TvProcessor(mock_tmdb).process(ctx)

    dest = tv_dir / "Breaking Bad (2008) [tmdbid-1396]" / "Season 01" / "Breaking Bad S01E01.mkv"
    assert dest.exists()


def test_no_tmdb_match(tv_dir, source_file):
    """No TMDB match — folder has no year or tmdb_id."""
    tmdb = MagicMock(spec=TMDBClient)
    tmdb.search_tv.return_value = (None, None)
    src = source_file("Unknown.Show.S01E01.mkv")
    ctx = _ctx(str(src), title="Unknown Show", season="01", episode="01")

    result = TvProcessor(tmdb).process(ctx)

    assert result.success is True
    dest = tv_dir / "Unknown Show" / "Season 01" / "Unknown Show S01E01.mkv"
    assert dest.exists()


def test_numeric_title_year_stripped(tv_dir, source_file, mock_tmdb):
    """When title == year (e.g. '1923'), year is removed from tokens."""
    mock_tmdb.search_tv.return_value = (123456, "1923")
    src = source_file("1923.S01E01.mkv")
    ctx = _ctx(str(src), title="1923", year="1923", season="01", episode="01")

    TvProcessor(mock_tmdb).process(ctx)

    # year removed → folder has no (year) segment
    show_dirs = list(tv_dir.iterdir())
    assert len(show_dirs) == 1
    assert "1923" in show_dirs[0].name
    assert "(1923)" not in show_dirs[0].name


def test_no_quality(tv_dir, source_file, mock_tmdb):
    """Quality absent — dash segment removed from filename."""
    src = source_file("Severance.S02E01.mkv")
    ctx = _ctx(str(src), title="Severance", year="2022", season="02", episode="01")
    mock_tmdb.search_tv.return_value = (99966, "2022")

    TvProcessor(mock_tmdb).process(ctx)

    dest = tv_dir / "Severance (2022) [tmdbid-99966]" / "Season 02" / "Severance S02E01.mkv"
    assert dest.exists()


# ---------------------------------------------------------------------------
# Dry run
# ---------------------------------------------------------------------------


def test_dry_run(tv_dir, source_file, mock_tmdb):
    config.DRY_RUN = True
    src = source_file("Show.S01E01.mkv")
    ctx = _ctx(str(src), title="Show", season="01", episode="01")

    result = TvProcessor(mock_tmdb).process(ctx)

    assert result.success is True
    assert not any(tv_dir.iterdir())  # no dirs or files created


# ---------------------------------------------------------------------------
# Error path
# ---------------------------------------------------------------------------


def test_source_missing(tv_dir, mock_tmdb):  # noqa: ARG001
    ctx = _ctx("/nonexistent/Show.S01E01.mkv", title="Show", season="01", episode="01")

    result = TvProcessor(mock_tmdb).process(ctx)

    assert result.success is False
