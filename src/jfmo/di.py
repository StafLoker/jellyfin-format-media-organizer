from .config import config
from .formatter import Formatter
from .metadata import TMDBClient
from .parser import Parser
from .parser.steps import (
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
from .processors import MovieProcessor, TvProcessor


class Container:
    def __init__(self) -> None:
        self.tmdb_client = TMDBClient(config.TMDB_API_KEY)

        self.parser = Parser(
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

        self.movie_processor = MovieProcessor(self.tmdb_client)
        self.tv_processor = TvProcessor(self.tmdb_client)

        self.formatter = Formatter(self.parser, self.movie_processor, self.tv_processor)
