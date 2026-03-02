from unittest.mock import MagicMock

import pytest

from jfmo.config import config
from jfmo.formatter import Formatter
from jfmo.metadata.tmdb import TMDBClient
from jfmo.parser import Parser
from jfmo.parser.steps import (
    EpisodeStep,
    ExtensionStep,
    MediaTypeStep,
    QualityStep,
    SeasonStep,
    TitleStep,
    YearStep,
)
from jfmo.processors import MovieProcessor, TvProcessor


@pytest.fixture
def media_dirs(tmp_path):
    films = tmp_path / "films"
    tv = tmp_path / "tv"
    films.mkdir()
    tv.mkdir()
    config.FILMS_DIR = str(films)
    config.TV_DIR = str(tv)
    config.DRY_RUN = False
    return films, tv


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
        QualityStep(),
        MediaTypeStep(),
        TitleStep(),
    )
    return Formatter(parser, MovieProcessor(mock_tmdb), TvProcessor(mock_tmdb))
