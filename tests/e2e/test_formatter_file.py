from pathlib import Path


def _src(tmp_path, filename: str) -> Path:
    src = tmp_path / "downloads" / filename
    src.parent.mkdir(exist_ok=True)
    src.write_bytes(b"\x00" * 1024)
    return src


# ---------------------------------------------------------------------------
# TV files
# ---------------------------------------------------------------------------


def test_tv_file(formatter, media_dirs, mock_tmdb, tmp_path):
    films_dir, tv_dir = media_dirs
    mock_tmdb.search_tv.return_value = (2316, "2005")
    src = _src(tmp_path, "The.Office.S03E07.720p.mkv")

    result = formatter.format_file(str(src))

    assert result is True
    dest = tv_dir / "The Office (2005) [tmdbid-2316]" / "Season 03" / "The Office S03E07 - [720p].mkv"
    assert dest.exists()
    assert dest.stat().st_ino == src.stat().st_ino


def test_tv_no_tmdb(formatter, media_dirs, mock_tmdb, tmp_path):
    """TV file without TMDB match — no year/id in folder name."""
    _, tv_dir = media_dirs
    mock_tmdb.search_tv.return_value = (None, None)
    src = _src(tmp_path, "Unknown.Show.S01E01.mkv")

    result = formatter.format_file(str(src))

    assert result is True
    dest = tv_dir / "Unknown Show" / "Season 01" / "Unknown Show S01E01.mkv"
    assert dest.exists()


def test_lostfilm_tags_stripped(formatter, media_dirs, mock_tmdb, tmp_path):
    """LostFilm release: rus and LostFilm.TV stripped by QualityStep."""
    _, tv_dir = media_dirs
    mock_tmdb.search_tv.return_value = (None, None)
    src = _src(tmp_path, "A.Knight.of.the.Seven.Kingdoms.S01E04.1080p.rus.LostFilm.TV.mkv")

    formatter.format_file(str(src))

    show_dirs = list(tv_dir.iterdir())
    assert len(show_dirs) == 1
    assert show_dirs[0].name.startswith("A Knight of the Seven Kingdoms")


# ---------------------------------------------------------------------------
# Movie files
# ---------------------------------------------------------------------------


def test_movie_file(formatter, media_dirs, mock_tmdb, tmp_path):
    films_dir, _ = media_dirs
    mock_tmdb.search_movie.return_value = (27205, "2010")
    src = _src(tmp_path, "Inception.2010.1080p.BluRay.mkv")

    result = formatter.format_file(str(src))

    assert result is True
    dest = films_dir / "Inception (2010) [tmdbid-27205] - [1080p].mkv"
    assert dest.exists()
    assert dest.stat().st_ino == src.stat().st_ino


def test_movie_tmdb_provides_year(formatter, media_dirs, mock_tmdb, tmp_path):
    """TMDB provides year when absent from filename."""
    films_dir, _ = media_dirs
    mock_tmdb.search_movie.return_value = (374720, "2017")
    src = _src(tmp_path, "Dunkirk.1080p.mkv")

    formatter.format_file(str(src))

    dest = films_dir / "Dunkirk (2017) [tmdbid-374720] - [1080p].mkv"
    assert dest.exists()


def test_movie_no_tmdb(formatter, media_dirs, mock_tmdb, tmp_path):
    """Movie without TMDB match — no tmdb_id in filename."""
    films_dir, _ = media_dirs
    mock_tmdb.search_movie.return_value = (None, "2010")
    src = _src(tmp_path, "Inception.2010.1080p.mkv")

    formatter.format_file(str(src))

    dest = films_dir / "Inception (2010) - [1080p].mkv"
    assert dest.exists()


# ---------------------------------------------------------------------------
# Skipped / edge cases
# ---------------------------------------------------------------------------


def test_ambiguous_returns_none(formatter, media_dirs, tmp_path):
    """Date-based filename is ambiguous → skipped, returns None."""
    films_dir, tv_dir = media_dirs
    src = _src(tmp_path, "Show.2024-01-15.mkv")

    result = formatter.format_file(str(src))

    assert result is None
    assert not any(films_dir.iterdir())
    assert not any(tv_dir.iterdir())


def test_dry_run(formatter, media_dirs, mock_tmdb, tmp_path):
    """Dry run returns True but creates no files."""
    from jfmo.config import config

    config.DRY_RUN = True
    films_dir, _ = media_dirs
    mock_tmdb.search_movie.return_value = (27205, "2010")
    src = _src(tmp_path, "Inception.2010.1080p.mkv")

    result = formatter.format_file(str(src))

    assert result is True
    assert not any(films_dir.iterdir())
