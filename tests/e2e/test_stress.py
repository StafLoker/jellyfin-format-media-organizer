import time
from pathlib import Path

from loguru import logger

MOVIE_NAMES = [
    "Inception.2010.1080p.BluRay.x264.mkv",
    "The.Dark.Knight.2008.720p.BluRay.mkv",
    "Interstellar.2014.2160p.UHD.BluRay.mkv",
    "Pulp.Fiction.1994.1080p.BluRay.mkv",
    "The.Matrix.1999.1080p.BluRay.x265.mkv",
    "Fight.Club.1999.720p.WEB-DL.mkv",
    "Forrest.Gump.1994.1080p.BluRay.mkv",
    "The.Shawshank.Redemption.1994.1080p.mkv",
    "Gladiator.2000.720p.BluRay.mkv",
    "The.Lord.of.the.Rings.2001.1080p.BluRay.mkv",
]

TV_NAMES = [
    "Breaking.Bad.S{season:02d}E{ep:02d}.1080p.BluRay.mkv",
    "The.Office.S{season:02d}E{ep:02d}.720p.WEB-DL.mkv",
    "Game.of.Thrones.S{season:02d}E{ep:02d}.1080p.BluRay.mkv",
    "Stranger.Things.S{season:02d}E{ep:02d}.2160p.WEB-DL.mkv",
    "The.Mandalorian.S{season:02d}E{ep:02d}.1080p.mkv",
]


logger.disable("jfmo")


def _create_files(directory: Path, filenames: list[str]) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for name in filenames:
        f = directory / name
        f.write_bytes(b"\x00" * 512)
        paths.append(f)
    return paths


# ---------------------------------------------------------------------------
# Stress: format_file with many movies
# ---------------------------------------------------------------------------


def test_stress_format_file_movies(formatter, media_dirs, mock_tmdb, tmp_path):  # noqa: ARG001
    """Measure time to format_file 100 movie files."""
    mock_tmdb.search_movie.return_value = (12345, "2010")
    count = 100
    src_dir = tmp_path / "downloads"

    filenames = [
        f"{name.rsplit('.', 1)[0]}.variant{i}.mkv" if i >= len(MOVIE_NAMES) else name
        for i, name in enumerate(MOVIE_NAMES * (count // len(MOVIE_NAMES) + 1))
    ][:count]

    paths = _create_files(src_dir, filenames)

    start = time.perf_counter()
    results = [formatter.format_file(str(p)) for p in paths]
    elapsed = time.perf_counter() - start

    processed = [r for r in results if r is not None]
    assert len(processed) == count
    print(f"\n  format_file x{count} movies: {elapsed:.3f}s ({elapsed / count * 1000:.1f}ms/file)")


# ---------------------------------------------------------------------------
# Stress: format_file with many TV episodes
# ---------------------------------------------------------------------------


def test_stress_format_file_tv(formatter, media_dirs, mock_tmdb, tmp_path):  # noqa: ARG001
    """Measure time to format_file 100 TV episode files."""
    mock_tmdb.search_tv.return_value = (1396, "2008")
    count = 100
    src_dir = tmp_path / "downloads"

    filenames = []
    for i in range(count):
        template = TV_NAMES[i % len(TV_NAMES)]
        filenames.append(template.format(season=(i // 10) + 1, ep=(i % 10) + 1))

    paths = _create_files(src_dir, filenames)

    start = time.perf_counter()
    results = [formatter.format_file(str(p)) for p in paths]
    elapsed = time.perf_counter() - start

    processed = [r for r in results if r is not None]
    assert len(processed) == count
    print(f"\n  format_file x{count} TV episodes: {elapsed:.3f}s ({elapsed / count * 1000:.1f}ms/file)")


# ---------------------------------------------------------------------------
# Stress: format_directory with a large season pack
# ---------------------------------------------------------------------------


def test_stress_format_directory_large_season(formatter, media_dirs, mock_tmdb, tmp_path):  # noqa: ARG001
    """Measure time to format_directory with 50 episodes in one dir."""
    mock_tmdb.search_tv.return_value = (1396, "2008")
    episode_count = 50
    show_dir = tmp_path / "downloads" / "Breaking.Bad.S01"
    show_dir.mkdir(parents=True)

    for i in range(1, episode_count + 1):
        (show_dir / f"Breaking.Bad.S01E{i:02d}.1080p.mkv").write_bytes(b"\x00" * 512)

    start = time.perf_counter()
    results = formatter.format_directory(str(show_dir))
    elapsed = time.perf_counter() - start

    assert len(results) == episode_count
    assert all(r.success for r in results)
    print(
        f"\n  format_directory x{episode_count} episodes (1 dir): {elapsed:.3f}s ({elapsed / episode_count * 1000:.1f}ms/file)"
    )


# ---------------------------------------------------------------------------
# Stress: format_directory with nested seasons
# ---------------------------------------------------------------------------


def test_stress_format_directory_multi_season(formatter, media_dirs, mock_tmdb, tmp_path):  # noqa: ARG001
    """Measure time to format_directory with 5 seasons x 20 episodes = 100 files."""
    mock_tmdb.search_tv.return_value = (1396, "2008")
    seasons = 5
    eps_per_season = 20
    total = seasons * eps_per_season

    show_dir = tmp_path / "downloads" / "Breaking.Bad"
    show_dir.mkdir(parents=True)

    for s in range(1, seasons + 1):
        season_dir = show_dir / f"S{s:02d}"
        season_dir.mkdir()
        for e in range(1, eps_per_season + 1):
            (season_dir / f"Breaking.Bad.S{s:02d}E{e:02d}.1080p.mkv").write_bytes(b"\x00" * 512)

    start = time.perf_counter()
    results = formatter.format_directory(str(show_dir))
    elapsed = time.perf_counter() - start

    assert len(results) == total
    assert all(r.success for r in results)
    print(
        f"\n  format_directory x{total} episodes ({seasons} seasons): {elapsed:.3f}s ({elapsed / total * 1000:.1f}ms/file)"
    )
