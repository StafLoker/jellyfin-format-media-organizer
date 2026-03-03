import pytest

from jfmo.utils.token_formatter import format_tokens

# Default patterns matching config defaults
MOVIE_PATTERN = "{title} ({year}) [tmdbid-{tmdb_id}] - {quality}"
TV_FOLDER_PATTERN = "{title} ({year}) [tmdbid-{tmdb_id}]"
TV_SEASON_PATTERN = "Season {season}"
TV_FILE_PATTERN = "{title} S{season}E{episode} - {quality}"


# ---------------------------------------------------------------------------
# Movie file
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "tokens, expected",
    [
        (
            {"title": "Inception", "year": "2010", "tmdb_id": "27205", "quality": "[1080p]"},
            "Inception (2010) [tmdbid-27205] - [1080p]",
        ),
        (
            {"title": "Inception", "year": "2010", "quality": "[1080p]"},  # no tmdb_id
            "Inception (2010) - [1080p]",
        ),
        (
            {"title": "Inception", "year": "2010", "tmdb_id": "27205"},  # no quality
            "Inception (2010) [tmdbid-27205]",
        ),
        (
            {"title": "Inception", "tmdb_id": "27205", "quality": "[1080p]"},  # no year
            "Inception [tmdbid-27205] - [1080p]",
        ),
        (
            {"title": "Inception"},  # only title
            "Inception",
        ),
    ],
)
def test_format_movie_file(tokens, expected):
    assert format_tokens(MOVIE_PATTERN, tokens) == expected


# ---------------------------------------------------------------------------
# TV folder
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "tokens, expected",
    [
        (
            {"title": "Breaking Bad", "year": "2008", "tmdb_id": "1396"},
            "Breaking Bad (2008) [tmdbid-1396]",
        ),
        (
            {"title": "Breaking Bad", "tmdb_id": "1396"},  # no year
            "Breaking Bad [tmdbid-1396]",
        ),
        (
            {"title": "Breaking Bad", "year": "2008"},  # no tmdb_id
            "Breaking Bad (2008)",
        ),
        (
            {"title": "Breaking Bad"},
            "Breaking Bad",
        ),
    ],
)
def test_format_tv_folder(tokens, expected):
    assert format_tokens(TV_FOLDER_PATTERN, tokens) == expected


# ---------------------------------------------------------------------------
# TV season folder
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "tokens, expected",
    [
        ({"season": "01"}, "Season 01"),
        ({"season": "12"}, "Season 12"),
    ],
)
def test_format_tv_season(tokens, expected):
    assert format_tokens(TV_SEASON_PATTERN, tokens) == expected


# ---------------------------------------------------------------------------
# TV file
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "tokens, expected",
    [
        (
            {"title": "Breaking Bad", "season": "01", "episode": "05", "quality": "[1080p]"},
            "Breaking Bad S01E05 - [1080p]",
        ),
        (
            {"title": "Breaking Bad", "season": "01", "episode": "05"},  # no quality
            "Breaking Bad S01E05",
        ),
        (
            {"title": "Severance", "season": "02", "episode": "01", "quality": "[2160p]"},
            "Severance S02E01 - [2160p]",
        ),
    ],
)
def test_format_tv_file(tokens, expected):
    assert format_tokens(TV_FILE_PATTERN, tokens) == expected


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_no_trailing_dash():
    result = format_tokens("{title} - {quality}", {"title": "Film"})
    assert result == "Film"
    assert not result.endswith(" -")


def test_no_leading_dash():
    result = format_tokens("{title} ({year})", {"title": "Film"})
    assert result == "Film"


def test_collapse_spaces():
    result = format_tokens("{title}  ({year})", {"title": "Film"})
    assert "  " not in result


def test_empty_string_token_treated_as_missing():
    result = format_tokens(MOVIE_PATTERN, {"title": "Film", "year": ""})
    assert result == "Film"
