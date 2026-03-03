import pytest

from jfmo.parser.context import MediaType, ParseContext
from jfmo.parser.steps import (
    CodecStep,
    EpisodeStep,
    ExtensionStep,
    HdrStep,
    MediaTypeStep,
    QualityStep,
    ReleaseGroupStep,
    SeasonStep,
    ServiceStep,
    SourceStep,
    TitleStep,
    YearStep,
)
from jfmo.parser.tokens import Token


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
    "filename, season, leftover_episode",
    [
        ("Show.S01E05.mkv", "01", "E05"),
        ("show.s02e10.mkv", "02", "E10"),
        ("Show.S01.E01.mkv", "01", "E01"),
        ("Show.3x07.mkv", "03", "E07"),
        ("Show.S01E01-E03.mkv", "01", "E01-E03"),
        ("Show.S12E24.mkv", "12", "E24"),
    ],
)
def test_season_extracts_season_leaves_episode(filename, season, leftover_episode):
    ctx = SeasonStep().process(_ctx(filename))
    assert ctx.tokens[Token.SEASON] == season
    assert Token.EPISODE not in ctx.tokens
    assert leftover_episode in ctx.working_name


def test_season_removes_season_marker_from_working_name():
    ctx = SeasonStep().process(_ctx("The.Office.S03E07.720p"))
    assert "S03" not in ctx.working_name
    assert "s03" not in ctx.working_name.lower().replace("e07", "")


def test_season_not_detected():
    ctx = SeasonStep().process(_ctx("Inception.2010.1080p.mkv"))
    assert Token.SEASON not in ctx.tokens


def test_standalone_season():
    """Standalone S02 pattern (e.g. directory name)."""
    ctx = SeasonStep().process(_ctx("Breaking.Bad.S02"))
    assert ctx.tokens[Token.SEASON] == "02"
    assert Token.EPISODE not in ctx.tokens
    assert "S02" not in ctx.working_name


# ---------------------------------------------------------------------------
# EpisodeStep
# ---------------------------------------------------------------------------


def test_episode_from_season_step_leftover():
    """EpisodeStep picks up the E05 leftover from SeasonStep."""
    ctx = _ctx("Show.E05.720p", season="01")
    ctx = EpisodeStep().process(ctx)
    assert ctx.tokens[Token.EPISODE] == "05"
    assert "E05" not in ctx.working_name


def test_episode_only_when_season_present():
    """When season comes from directory seed, detect episode-only pattern."""
    ctx = _ctx("Show.E05.mkv", season="02")
    ctx = EpisodeStep().process(ctx)
    assert ctx.tokens[Token.EPISODE] == "05"
    assert ctx.tokens[Token.SEASON] == "02"


def test_episode_skipped_without_season():
    """No season → EpisodeStep does nothing."""
    ctx = _ctx("Show.E05.mkv")
    ctx = EpisodeStep().process(ctx)
    assert Token.EPISODE not in ctx.tokens


def test_episode_skipped_when_already_present():
    """Episode already set → EpisodeStep does nothing."""
    ctx = _ctx("Show.E05.mkv", season="01", episode="03")
    ctx = EpisodeStep().process(ctx)
    assert ctx.tokens[Token.EPISODE] == "03"  # unchanged


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
    assert ctx.tokens[Token.YEAR] == year


def test_year_removes_from_working_name():
    ctx = YearStep().process(_ctx("Movie.2010.1080p"))
    assert "2010" not in ctx.working_name


def test_year_not_detected():
    ctx = YearStep().process(_ctx("Show.S01E01.mkv"))
    assert Token.YEAR not in ctx.tokens


# ---------------------------------------------------------------------------
# SourceStep
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename, source",
    [
        ("Movie.WEB-DL.1080p", "WEB-DL"),
        ("Movie.BluRay.x265", "BluRay"),
        ("Movie.BDRip.1080p", "BDRip"),
        ("Movie.HDTV.720p", "HDTV"),
        ("Movie.DVDRip.mkv", "DVDRip"),
        ("Movie.WEBRip.mkv", "WEBRip"),
    ],
)
def test_source_detected(filename, source):
    ctx = SourceStep().process(_ctx(filename))
    assert ctx.tokens[Token.SOURCE] == source


def test_source_removes_from_working_name():
    ctx = SourceStep().process(_ctx("Movie.WEB-DL.1080p"))
    assert "WEB-DL" not in ctx.working_name


def test_source_not_detected():
    ctx = SourceStep().process(_ctx("Movie.1080p.mkv"))
    assert Token.SOURCE not in ctx.tokens


# ---------------------------------------------------------------------------
# CodecStep
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename, codec",
    [
        ("Movie.x265.mkv", "x265"),
        ("Movie.x264.mkv", "x264"),
        ("Movie.HEVC.mkv", "HEVC"),
        ("Movie.H.265.mkv", "H.265"),
        ("Movie.H264.mkv", "H264"),
        ("Movie.AV1.mkv", "AV1"),
    ],
)
def test_codec_detected(filename, codec):
    ctx = CodecStep().process(_ctx(filename))
    assert ctx.tokens[Token.CODEC] == codec


def test_codec_removes_from_working_name():
    ctx = CodecStep().process(_ctx("Movie.x265.1080p"))
    assert "x265" not in ctx.working_name


def test_codec_not_detected():
    ctx = CodecStep().process(_ctx("Movie.1080p.mkv"))
    assert Token.CODEC not in ctx.tokens


# ---------------------------------------------------------------------------
# HdrStep
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename, hdr",
    [
        ("Movie.HDR.mkv", "HDR"),
        ("Movie.HDR10.mkv", "HDR10"),
        ("Movie.DV.mkv", "DV"),
        ("Movie.DoVi.mkv", "DoVi"),
        ("Movie.SDR.mkv", "SDR"),
    ],
)
def test_hdr_detected(filename, hdr):
    ctx = HdrStep().process(_ctx(filename))
    assert ctx.tokens[Token.HDR] == hdr


def test_hdr_removes_from_working_name():
    ctx = HdrStep().process(_ctx("Movie.DV.1080p"))
    assert "DV" not in ctx.working_name


def test_hdr_not_detected():
    ctx = HdrStep().process(_ctx("Movie.1080p.mkv"))
    assert Token.HDR not in ctx.tokens


# ---------------------------------------------------------------------------
# ServiceStep
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename, service",
    [
        ("Movie.NF.WEB-DL", "NF"),
        ("Movie.AMZN.WEBRip", "AMZN"),
        ("Movie.DSNP.1080p", "DSNP"),
        ("Movie.HMAX.mkv", "HMAX"),
        ("Movie.ATVP.mkv", "ATVP"),
    ],
)
def test_service_detected(filename, service):
    ctx = ServiceStep().process(_ctx(filename))
    assert ctx.tokens[Token.SERVICE] == service


def test_service_removes_from_working_name():
    ctx = ServiceStep().process(_ctx("Movie.NF.WEB-DL"))
    assert "NF" not in ctx.working_name


def test_service_not_detected():
    ctx = ServiceStep().process(_ctx("Movie.WEB-DL.1080p"))
    assert Token.SERVICE not in ctx.tokens


# ---------------------------------------------------------------------------
# ReleaseGroupStep
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "working_name, release_group",
    [
        ("Movie.DV-TheEqualizer", "TheEqualizer"),
        ("Movie-NOOBDL", "NOOBDL"),
        ("Show.1080p.rus-LostFilm", "LostFilm"),
    ],
)
def test_release_group_detected(working_name, release_group):
    ctx = ParseContext(filepath="/downloads/x.mkv", working_name=working_name)
    ctx = ReleaseGroupStep().process(ctx)
    assert ctx.tokens[Token.RELEASE_GROUP] == release_group


def test_release_group_removes_from_working_name():
    ctx = ParseContext(filepath="/downloads/x.mkv", working_name="Movie-NOOBDL")
    ctx = ReleaseGroupStep().process(ctx)
    assert "NOOBDL" not in ctx.working_name
    assert ctx.working_name == "Movie"


def test_release_group_not_detected():
    ctx = ParseContext(filepath="/downloads/x.mkv", working_name="Movie.1080p")
    ctx = ReleaseGroupStep().process(ctx)
    assert Token.RELEASE_GROUP not in ctx.tokens


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
    assert ctx.tokens[Token.QUALITY] == quality


def test_quality_strips_tags_from_working_name():
    ctx = QualityStep().process(_ctx("The.Office.1080p.rus"))
    assert "1080p" not in ctx.working_name
    assert "rus" not in ctx.working_name


def test_quality_not_detected():
    ctx = QualityStep().process(_ctx("Movie.no.quality.mkv"))
    assert Token.QUALITY not in ctx.tokens


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
    assert ctx.tokens[Token.TITLE] == expected_title


# ---------------------------------------------------------------------------
# Full pipeline integration (chained steps)
# ---------------------------------------------------------------------------


def _full_pipeline():
    from jfmo.parser import Parser

    return Parser(
        ExtensionStep(),
        SeasonStep(),
        EpisodeStep(),
        YearStep(),
        SourceStep(),
        CodecStep(),
        HdrStep(),
        ServiceStep(),
        ReleaseGroupStep(),
        QualityStep(),
        MediaTypeStep(),
        TitleStep(),
    )


def test_pipeline_tv_episode():
    """Full chain on a typical TV filename."""
    ctx = _full_pipeline().parse("/downloads/The.Office.S03E07.720p.BluRay.mkv")

    assert ctx.tokens[Token.SEASON] == "03"
    assert ctx.tokens[Token.EPISODE] == "07"
    assert ctx.tokens[Token.QUALITY] == "[720p]"
    assert ctx.tokens[Token.SOURCE] == "BluRay"
    assert ctx.tokens[Token.TITLE] == "The Office"
    assert ctx.extension == ".mkv"
    assert ctx.media_type == MediaType.TV


def test_pipeline_movie():
    """Full chain on a typical movie filename."""
    ctx = _full_pipeline().parse("/downloads/Inception.2010.1080p.BluRay.mkv")

    assert ctx.tokens[Token.YEAR] == "2010"
    assert ctx.tokens[Token.QUALITY] == "[1080p]"
    assert ctx.tokens[Token.SOURCE] == "BluRay"
    assert ctx.tokens[Token.TITLE] == "Inception"
    assert ctx.extension == ".mkv"
    assert ctx.media_type == MediaType.MOVIE


def test_pipeline_lostfilm():
    """LostFilm release: all tags cleaned properly."""
    ctx = _full_pipeline().parse("/downloads/A.Knight.of.the.Seven.Kingdoms.S01E04.1080p.rus.LostFilm.TV.mkv")

    assert ctx.tokens[Token.SEASON] == "01"
    assert ctx.tokens[Token.EPISODE] == "04"
    assert ctx.tokens[Token.QUALITY] == "[1080p]"
    assert ctx.tokens[Token.TITLE] == "A Knight of the Seven Kingdoms"
    assert ctx.media_type == MediaType.TV


def test_pipeline_frankenstein_nf():
    """NF service and WEB-DL source cleaned from title."""
    ctx = _full_pipeline().parse("/downloads/Frankenstein.2025.NF.WEB-DL.2160p.mkv")

    assert ctx.tokens[Token.TITLE] == "Frankenstein"
    assert ctx.tokens[Token.SERVICE] == "NF"
    assert ctx.tokens[Token.SOURCE] == "WEB-DL"
    assert ctx.tokens[Token.QUALITY] == "[2160p]"
    assert ctx.tokens[Token.YEAR] == "2025"


def test_pipeline_white_bird_dv_release_group():
    """DV hdr and release group extracted."""
    ctx = _full_pipeline().parse("/downloads/White.Bird.2023.2160p.WEB-DL.DV-TheEqualizer.mp4")

    assert ctx.tokens[Token.TITLE] == "White Bird"
    assert ctx.tokens[Token.YEAR] == "2023"
    assert ctx.tokens[Token.HDR] == "DV"
    assert ctx.tokens[Token.RELEASE_GROUP] == "TheEqualizer"
    assert ctx.tokens[Token.SOURCE] == "WEB-DL"
    assert ctx.tokens[Token.QUALITY] == "[2160p]"


def test_pipeline_mollys_game_bdrip():
    """BDRip source extracted."""
    ctx = _full_pipeline().parse("/downloads/Mollys Game 2017 BDRip 1080p.mkv")

    assert ctx.tokens[Token.TITLE] == "Mollys Game"
    assert ctx.tokens[Token.SOURCE] == "BDRip"
    assert ctx.tokens[Token.YEAR] == "2017"
    assert ctx.tokens[Token.QUALITY] == "[1080p]"


def test_pipeline_ambiguous_skips():
    """Ambiguous pattern stops pipeline and sets skip_reason."""
    ctx = _full_pipeline().parse("/downloads/Show.2024-01-15.mkv")

    assert ctx.skip_reason is not None
    assert ctx.media_type == MediaType.AMBIGUOUS


def test_pipeline_dirname():
    """Pipeline correctly parses a directory name (no extension, standalone season)."""
    ctx = _full_pipeline().parse("Breaking.Bad.S02")

    assert ctx.tokens[Token.SEASON] == "02"
    assert ctx.tokens[Token.TITLE] == "Breaking Bad"
    assert Token.EPISODE not in ctx.tokens
