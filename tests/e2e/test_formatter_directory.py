from pathlib import Path


def _show_dir(tmp_path, dirname: str, filenames: list[str]) -> Path:
    d = tmp_path / "downloads" / dirname
    d.mkdir(parents=True)
    for name in filenames:
        (d / name).write_bytes(b"\x00" * 512)
    return d


# ---------------------------------------------------------------------------
# Season from directory name
# ---------------------------------------------------------------------------


def test_season_from_dirname(formatter, media_dirs, mock_tmdb, tmp_path):
    """Season seeded from directory name — all episodes processed."""
    _, tv_dir = media_dirs
    mock_tmdb.search_tv.return_value = (1396, "2008")
    dirpath = _show_dir(tmp_path, "Breaking.Bad.S02", ["E01.mkv", "E02.mkv", "E03.mkv"])

    result = formatter.format_directory(str(dirpath))

    assert any(r.success for r in result)
    season_dir = tv_dir / "Breaking Bad (2008) [tmdbid-1396]" / "Season 02"
    assert season_dir.is_dir()
    assert len(list(season_dir.iterdir())) == 3


def test_season_from_filenames(formatter, media_dirs, mock_tmdb, tmp_path):
    """No season in dirname — season extracted from each filename."""
    _, tv_dir = media_dirs
    mock_tmdb.search_tv.return_value = (1396, "2008")
    dirpath = _show_dir(tmp_path, "Breaking.Bad", ["S01E01.mkv", "S01E02.mkv"])

    formatter.format_directory(str(dirpath))

    season_dir = tv_dir / "Breaking Bad (2008) [tmdbid-1396]" / "Season 01"
    assert season_dir.is_dir()
    assert len(list(season_dir.iterdir())) == 2


# ---------------------------------------------------------------------------
# Non-video files ignored
# ---------------------------------------------------------------------------


def test_non_video_files_skipped(formatter, media_dirs, mock_tmdb, tmp_path):
    """Non-video files (jpg, nfo) are ignored."""
    _, tv_dir = media_dirs
    mock_tmdb.search_tv.return_value = (5678, "2020")
    dirpath = _show_dir(tmp_path, "Show.S01", ["E01.mkv", "cover.jpg", "show.nfo"])

    formatter.format_directory(str(dirpath))

    all_files = list(tv_dir.rglob("*"))
    video_files = [f for f in all_files if f.is_file()]
    assert len(video_files) == 1
    assert video_files[0].suffix == ".mkv"


# ---------------------------------------------------------------------------
# Ambiguous files skipped without crashing
# ---------------------------------------------------------------------------


def test_ambiguous_file_skipped(formatter, media_dirs, mock_tmdb, tmp_path):
    """Ambiguous file produces no link but does not crash other files."""
    _, tv_dir = media_dirs
    mock_tmdb.search_tv.return_value = (5678, "2020")
    dirpath = _show_dir(tmp_path, "Show.S01", ["S01E01.mkv", "Show.2024-01-15.mkv"])

    result = formatter.format_directory(str(dirpath))

    assert any(r.success for r in result)  # at least one succeeded
    video_files = list(tv_dir.rglob("*.mkv"))
    assert len(video_files) == 1  # only the unambiguous one


# ---------------------------------------------------------------------------
# Empty directory
# ---------------------------------------------------------------------------


def test_empty_directory(formatter, media_dirs, tmp_path):  # noqa: ARG001
    """Empty directory returns False (no files processed)."""
    dirpath = tmp_path / "downloads" / "Empty.Show.S01"
    dirpath.mkdir(parents=True)

    result = formatter.format_directory(str(dirpath))

    assert result == []


# ---------------------------------------------------------------------------
# Dry run
# ---------------------------------------------------------------------------


def test_dry_run(formatter, media_dirs, mock_tmdb, tmp_path):
    """Dry run returns True but creates no files."""
    from jfmo.config import config

    config.DRY_RUN = True
    _, tv_dir = media_dirs
    mock_tmdb.search_tv.return_value = (1396, "2008")
    dirpath = _show_dir(tmp_path, "Breaking.Bad.S01", ["E01.mkv", "E02.mkv"])

    result = formatter.format_directory(str(dirpath))

    assert any(r.success for r in result)
    assert not any(tv_dir.iterdir())
