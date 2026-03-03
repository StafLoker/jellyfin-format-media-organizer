from pathlib import Path


def _show_dir(tmp_path, dirname: str, filenames: list[str]) -> Path:
    d = tmp_path / "downloads" / dirname
    d.mkdir(parents=True)
    for name in filenames:
        (d / name).write_bytes(b"\x00" * 512)
    return d


def _nested_show_dir(tmp_path, dirname: str, seasons: dict[str, list[str]]) -> Path:
    """Create a show directory with season subdirectories: {season_name: [filenames]}."""
    d = tmp_path / "downloads" / dirname
    d.mkdir(parents=True)
    for season, files in seasons.items():
        season_dir = d / season
        season_dir.mkdir()
        for name in files:
            (season_dir / name).write_bytes(b"\x00" * 512)
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
# Nested season subdirectories: Show/{S01,S02}/{files}
# ---------------------------------------------------------------------------


def test_nested_season_subdirs_with_sxxexx_in_filename(formatter, media_dirs, mock_tmdb, tmp_path):
    """Show/S01/Show.S01E01.mkv — SxxExx in filename, season subdir is redundant but harmless."""
    _, tv_dir = media_dirs
    mock_tmdb.search_tv.return_value = (1396, "2008")
    dirpath = _nested_show_dir(
        tmp_path,
        "Breaking.Bad",
        {
            "S01": ["Breaking.Bad.S01E01.720p.mkv", "Breaking.Bad.S01E02.720p.mkv"],
            "S02": ["Breaking.Bad.S02E01.720p.mkv"],
        },
    )

    result = formatter.format_directory(str(dirpath))

    assert len(result) == 3
    assert all(r.success for r in result)
    s1 = tv_dir / "Breaking Bad (2008) [tmdbid-1396]" / "Season 01"
    s2 = tv_dir / "Breaking Bad (2008) [tmdbid-1396]" / "Season 02"
    assert len(list(s1.iterdir())) == 2
    assert len(list(s2.iterdir())) == 1


def test_nested_season_subdirs_episode_only_filenames(formatter, media_dirs, mock_tmdb, tmp_path):
    """Show/S01/E01.mkv — season comes from subdir name, not filename."""
    _, tv_dir = media_dirs
    mock_tmdb.search_tv.return_value = (1396, "2008")
    dirpath = _nested_show_dir(
        tmp_path,
        "Breaking.Bad",
        {
            "S01": ["E01.mkv", "E02.mkv"],
            "S02": ["E01.mkv"],
        },
    )

    result = formatter.format_directory(str(dirpath))

    assert len(result) == 3
    assert all(r.success for r in result)
    s1 = tv_dir / "Breaking Bad (2008) [tmdbid-1396]" / "Season 01"
    s2 = tv_dir / "Breaking Bad (2008) [tmdbid-1396]" / "Season 02"
    assert len(list(s1.iterdir())) == 2
    assert len(list(s2.iterdir())) == 1


def test_nested_mixed_seasons(formatter, media_dirs, mock_tmdb, tmp_path):
    """Mix: one season has SxxExx in filenames, another has bare episode numbers."""
    _, tv_dir = media_dirs
    mock_tmdb.search_tv.return_value = (1396, "2008")
    dirpath = _nested_show_dir(
        tmp_path,
        "Breaking.Bad",
        {
            "S01": ["Breaking.Bad.S01E01.mkv", "Breaking.Bad.S01E02.mkv"],
            "S02": ["E01.mkv", "E02.mkv"],
        },
    )

    result = formatter.format_directory(str(dirpath))

    assert len(result) == 4
    assert all(r.success for r in result)
    s1 = tv_dir / "Breaking Bad (2008) [tmdbid-1396]" / "Season 01"
    s2 = tv_dir / "Breaking Bad (2008) [tmdbid-1396]" / "Season 02"
    assert len(list(s1.iterdir())) == 2
    assert len(list(s2.iterdir())) == 2


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
