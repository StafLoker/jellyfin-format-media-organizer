import pytest

from jfmo.parser.context import MediaType, ParseContext
from jfmo.parser.steps import (
    EpisodeStep,
    ExtensionStep,
    MediaTypeStep,
    QualityStep,
    SeasonStep,
    TitleStep,
    YearStep,
)


def _ctx(filename: str, **tokens) -> ParseContext:
    """Build a ParseContext with working_name pre-set."""
    return ParseContext(filepath=f"/downloads/{filename}", working_name=filename, tokens=dict(tokens))


# ---------------------------------------------------------------------------
# ExtensionStep
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename, expected_stem, expected_ext",
    [
        ("Show.S01E01.mkv", "Show.S01E01", ".mkv"),
        ("Movie.2024.1080p.mp4", "Movie.2024.1080p", ".mp4"),
        ("file.no.ext", "file.no.ext", ""),  # unknown extension not stripped
    ],
)
def test_extension_step(filename, expected_stem, expected_ext):
    ctx = ExtensionStep().process(_ctx(filename))
    assert ctx.extension == expected_ext
    assert ctx.working_name == expected_stem


# ---------------------------------------------------------------------------
# SeasonStep
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename, season, episode",
    [
        ("Show.S01E05.mkv", "01", "05"),
        ("show.s02e10.mkv", "02", "10"),
        ("Show.S01.E01.mkv", "01", "01"),
        ("Show.3x07.mkv", "03", "07"),
        ("Show.S01E01-E03.mkv", "01", "01"),
        ("Show.S12E24.mkv", "12", "24"),
    ],
)
def test_season_episode_detected(filename, season, episode):
    ctx = SeasonStep().process(_ctx(filename))
    assert ctx.tokens["season"] == season
    assert ctx.tokens["episode"] == episode


def test_season_removes_from_working_name():
    ctx = SeasonStep().process(_ctx("The.Office.S03E07.720p"))
    assert "S03E07" not in ctx.working_name
    assert "s03e07" not in ctx.working_name.lower()


def test_season_not_detected():
    ctx = SeasonStep().process(_ctx("Inception.2010.1080p.mkv"))
    assert "season" not in ctx.tokens
    assert "episode" not in ctx.tokens


def test_standalone_season():
    """Standalone S02 pattern (e.g. directory name)."""
    ctx = SeasonStep().process(_ctx("Breaking.Bad.S02"))
    assert ctx.tokens["season"] == "02"
    assert "episode" not in ctx.tokens
    assert "S02" not in ctx.working_name


# ---------------------------------------------------------------------------
# EpisodeStep
# ---------------------------------------------------------------------------


def test_episode_only_when_season_present():
    """When season comes from directory seed, detect episode-only pattern."""
    ctx = _ctx("Show.E05.mkv", season="02")
    ctx = EpisodeStep().process(ctx)
    assert ctx.tokens["episode"] == "05"
    assert ctx.tokens["season"] == "02"


def test_episode_skipped_without_season():
    """No season → EpisodeStep does nothing."""
    ctx = _ctx("Show.E05.mkv")
    ctx = EpisodeStep().process(ctx)
    assert "episode" not in ctx.tokens


def test_episode_skipped_when_already_present():
    """Episode already set by SeasonStep → EpisodeStep does nothing."""
    ctx = _ctx("Show.E05.mkv", season="01", episode="03")
    ctx = EpisodeStep().process(ctx)
    assert ctx.tokens["episode"] == "03"  # unchanged


# ---------------------------------------------------------------------------
# YearStep
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename, year",
    [
        ("Movie.2024.mkv", "2024"),
        ("Movie.1999.1080p", "1999"),
        ("Movie.2010.BluRay", "2010"),
    ],
)
def test_year_detected(filename, year):
    ctx = YearStep().process(_ctx(filename))
    assert ctx.tokens["year"] == year


def test_year_removes_from_working_name():
    ctx = YearStep().process(_ctx("Movie.2010.1080p"))
    assert "2010" not in ctx.working_name


def test_year_not_detected():
    ctx = YearStep().process(_ctx("Show.S01E01.mkv"))
    assert "year" not in ctx.tokens


# ---------------------------------------------------------------------------
# QualityStep
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename, quality",
    [
        ("Show.S01E01.720p.mkv", "[720p]"),
        ("Movie.2024.1080p.mkv", "[1080p]"),
        ("Movie.2160p.mkv", "[2160p]"),
        ("Movie.4K.mkv", "[2160p]"),
        ("Movie.UHD.mkv", "[2160p]"),
        ("Movie.FHD.mkv", "[1080p]"),
        ("Movie.HD.mkv", "[720p]"),
    ],
)
def test_quality_detected(filename, quality):
    ctx = QualityStep().process(_ctx(filename))
    assert ctx.tokens["quality"] == quality


def test_quality_strips_tags_from_working_name():
    ctx = QualityStep().process(_ctx("The.Office.S03E07.1080p.BluRay.x265.rus"))
    assert "1080p" not in ctx.working_name
    assert "BluRay" not in ctx.working_name
    assert "x265" not in ctx.working_name
    assert "rus" not in ctx.working_name


def test_quality_not_detected():
    ctx = QualityStep().process(_ctx("Movie.no.quality.mkv"))
    assert "quality" not in ctx.tokens


# ---------------------------------------------------------------------------
# MediaTypeStep
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename, expected_type",
    [
        ("Severance.S02E02.1080p.mkv", MediaType.TV),
        ("breaking.bad.s01e05.mkv", MediaType.TV),
        ("Show.3x07.mkv", MediaType.TV),
        ("Show.S01E01-E03.mkv", MediaType.TV),
        ("1923.S01E01.mkv", MediaType.TV),
        ("Inception.2010.1080p.BluRay.mkv", MediaType.MOVIE),
        ("The.Accountant.2.2024.2160p.mkv", MediaType.MOVIE),
        ("Inception.mkv", MediaType.MOVIE),
    ],
)
def test_media_type(filename, expected_type):
    ctx = MediaTypeStep().process(_ctx(filename))
    assert ctx.media_type == expected_type


def test_media_type_tv_from_token():
    """season token from directory seed → classified as TV when filename is unambiguous."""
    ctx = _ctx("Show.E05.mkv", season="02")
    ctx = MediaTypeStep().process(ctx)
    assert ctx.media_type == MediaType.TV


@pytest.mark.parametrize(
    "filename",
    [
        "Show.2024-01-15.mkv",  # date-based
    ],
)
def test_media_type_ambiguous(filename):
    ctx = MediaTypeStep().process(_ctx(filename))
    assert ctx.media_type == MediaType.AMBIGUOUS
    assert ctx.skip_reason is not None


# ---------------------------------------------------------------------------
# TitleStep
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "working_name, expected_title",
    [
        ("The.Office.US", "The Office US"),
        ("Breaking_Bad", "Breaking Bad"),
        ("Show-Name", "Show Name"),
        ("Show [NOOBDL]", "Show"),
        ("Show (Director's Cut)", "Show"),
        ("Show.2024-01-15", "Show"),  # date pattern removed
        ("  extra   spaces  ", "extra spaces"),
    ],
)
def test_title_step(working_name, expected_title):
    ctx = ParseContext(filepath="/downloads/x.mkv", working_name=working_name)
    ctx = TitleStep().process(ctx)
    assert ctx.tokens["title"] == expected_title


# ---------------------------------------------------------------------------
# Full pipeline integration (chained steps)
# ---------------------------------------------------------------------------


def test_pipeline_tv_episode():
    """Full chain on a typical TV filename."""
    from jfmo.parser import Parser

    parser = Parser(ExtensionStep(), SeasonStep(), EpisodeStep(), YearStep(), QualityStep(), MediaTypeStep(), TitleStep())
    ctx = parser.parse("/downloads/The.Office.S03E07.720p.BluRay.mkv")

    assert ctx.tokens["season"] == "03"
    assert ctx.tokens["episode"] == "07"
    assert ctx.tokens["quality"] == "[720p]"
    assert ctx.tokens["title"] == "The Office"
    assert ctx.extension == ".mkv"
    assert ctx.media_type == MediaType.TV


def test_pipeline_movie():
    """Full chain on a typical movie filename."""
    from jfmo.parser import Parser

    parser = Parser(ExtensionStep(), SeasonStep(), EpisodeStep(), YearStep(), QualityStep(), MediaTypeStep(), TitleStep())
    ctx = parser.parse("/downloads/Inception.2010.1080p.BluRay.mkv")

    assert ctx.tokens["year"] == "2010"
    assert ctx.tokens["quality"] == "[1080p]"
    assert ctx.tokens["title"] == "Inception"
    assert ctx.extension == ".mkv"
    assert ctx.media_type == MediaType.MOVIE


def test_pipeline_lostfilm():
    """LostFilm release: quality strips rus and LostFilm tags."""
    from jfmo.parser import Parser

    parser = Parser(ExtensionStep(), SeasonStep(), EpisodeStep(), YearStep(), QualityStep(), MediaTypeStep(), TitleStep())
    ctx = parser.parse("/downloads/A.Knight.of.the.Seven.Kingdoms.S01E04.1080p.rus.LostFilm.TV.mkv")

    assert ctx.tokens["season"] == "01"
    assert ctx.tokens["episode"] == "04"
    assert ctx.tokens["quality"] == "[1080p]"
    assert ctx.tokens["title"] == "A Knight of the Seven Kingdoms"
    assert ctx.media_type == MediaType.TV


def test_pipeline_ambiguous_skips():
    """Ambiguous pattern stops pipeline and sets skip_reason."""
    from jfmo.parser import Parser

    parser = Parser(ExtensionStep(), SeasonStep(), EpisodeStep(), YearStep(), QualityStep(), MediaTypeStep(), TitleStep())
    ctx = parser.parse("/downloads/Show.2024-01-15.mkv")

    assert ctx.skip_reason is not None
    assert ctx.media_type == MediaType.AMBIGUOUS


def test_pipeline_dirname():
    """Pipeline correctly parses a directory name (no extension, standalone season)."""
    from jfmo.parser import Parser

    parser = Parser(ExtensionStep(), SeasonStep(), EpisodeStep(), YearStep(), QualityStep(), MediaTypeStep(), TitleStep())
    ctx = parser.parse("Breaking.Bad.S02")

    assert ctx.tokens["season"] == "02"
    assert ctx.tokens["title"] == "Breaking Bad"
    assert "episode" not in ctx.tokens
