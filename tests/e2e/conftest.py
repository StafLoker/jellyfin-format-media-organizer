from unittest.mock import MagicMock

import pytest

from jfmo.config import config
from jfmo.formatter import Formatter
from jfmo.metadata.tmdb import TMDBClient
from jfmo.parser import Parser
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
from jfmo.processors import MovieProcessor, TvProcessor


@pytest.fixture
def media_dirs(tmp_path):
    movies = tmp_path / "movies"
    tv = tmp_path / "tv"
    movies.mkdir()
    tv.mkdir()
    config.MOVIES_DIR = str(movies)
    config.TV_DIR = str(tv)
    config.DRY_RUN = False
    return movies, tv


@pytest.fixture
def mock_tmdb():
    tmdb = MagicMock(spec=TMDBClient)
    tmdb.search_movie.return_value = (None, None)
    tmdb.search_tv.return_value = (None, None)
    return tmdb


@pytest.fixture
def formatter(mock_tmdb):
    parser = Parser(
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
    return Formatter(parser, MovieProcessor(mock_tmdb), TvProcessor(mock_tmdb))
