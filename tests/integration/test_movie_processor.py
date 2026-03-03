from pathlib import Path
from unittest.mock import MagicMock

import pytest

from jfmo.config import config
from jfmo.metadata.tmdb import TMDBClient
from jfmo.parser.context import MediaType, ParseContext
from jfmo.processors.movie_processor import MovieProcessor


@pytest.fixture
def movies_dir(tmp_path):
    d = tmp_path / "movies"
    d.mkdir()
    config.MOVIES_DIR = str(d)
    config.DRY_RUN = False
    config.FORMAT_MOVIE_FILE = "{title} ({year}) [tmdbid-{tmdb_id}] - {quality}"
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
    tmdb.search_movie.return_value = (27205, "2010")
    return tmdb


def _ctx(filepath: str, **tokens) -> ParseContext:
    return ParseContext(
        filepath=filepath,
        extension=Path(filepath).suffix,
        media_type=MediaType.MOVIE,
        tokens=dict(tokens),
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_all_tokens(movies_dir, source_file, mock_tmdb):
    src = source_file("Inception.2010.1080p.mkv")
    ctx = _ctx(str(src), title="Inception", year="2010", quality="[1080p]")

    result = MovieProcessor(mock_tmdb).process(ctx)

    assert result.success is True
    dest = movies_dir / "Inception (2010) [tmdbid-27205] - [1080p].mkv"
    assert dest.exists()
    assert dest.stat().st_ino == src.stat().st_ino  # hard link


def test_tmdb_provides_year(movies_dir, source_file, mock_tmdb):
    """TMDB result year is used when file had none."""
    mock_tmdb.search_movie.return_value = (27205, "2010")
    src = source_file("Inception.1080p.mkv")
    ctx = _ctx(str(src), title="Inception", quality="[1080p]")

    MovieProcessor(mock_tmdb).process(ctx)

    dest = movies_dir / "Inception (2010) [tmdbid-27205] - [1080p].mkv"
    assert dest.exists()


def test_no_tmdb_match(movies_dir, source_file):
    """No TMDB match — tmdb_id segment removed from filename."""
    tmdb = MagicMock(spec=TMDBClient)
    tmdb.search_movie.return_value = (None, "2023")
    src = source_file("Obscure.Film.2023.mkv")
    ctx = _ctx(str(src), title="Obscure Film", year="2023")

    result = MovieProcessor(tmdb).process(ctx)

    assert result.success is True
    dest = movies_dir / "Obscure Film (2023).mkv"
    assert dest.exists()


def test_no_quality(movies_dir, source_file, mock_tmdb):
    """Quality token absent — dash segment removed."""
    src = source_file("Inception.2010.mkv")
    ctx = _ctx(str(src), title="Inception", year="2010")

    MovieProcessor(mock_tmdb).process(ctx)

    dest = movies_dir / "Inception (2010) [tmdbid-27205].mkv"
    assert dest.exists()


def test_dest_already_exists_overwritten(movies_dir, source_file, mock_tmdb):
    """Existing destination is replaced with new hard link."""
    src = source_file("Inception.2010.1080p.mkv")
    ctx = _ctx(str(src), title="Inception", year="2010", quality="[1080p]")
    dest = movies_dir / "Inception (2010) [tmdbid-27205] - [1080p].mkv"
    dest.write_bytes(b"old content")
    old_ino = dest.stat().st_ino

    MovieProcessor(mock_tmdb).process(ctx)

    assert dest.stat().st_ino != old_ino
    assert dest.stat().st_ino == src.stat().st_ino


# ---------------------------------------------------------------------------
# Dry run
# ---------------------------------------------------------------------------


def test_dry_run(movies_dir, source_file, mock_tmdb):
    config.DRY_RUN = True
    src = source_file("Inception.2010.1080p.mkv")
    ctx = _ctx(str(src), title="Inception", year="2010", quality="[1080p]")

    result = MovieProcessor(mock_tmdb).process(ctx)

    assert result.success is True
    assert not any(movies_dir.iterdir())  # no file created


# ---------------------------------------------------------------------------
# Error path
# ---------------------------------------------------------------------------


def test_source_missing(movies_dir, mock_tmdb):  # noqa: ARG001
    ctx = _ctx("/nonexistent/Inception.mkv", title="Inception")

    result = MovieProcessor(mock_tmdb).process(ctx)

    assert result.success is False
