import os

from loguru import logger

from .parser import MediaType, ParseContext, Parser
from .processors.movie_processor import MovieProcessor
from .processors.tv_processor import TvProcessor
from .transliteration import Transliterator
from .utils.fs.file_ops import is_video_file


class Formatter:
    def __init__(self, parser: Parser, movie_processor: MovieProcessor, tv_processor: TvProcessor) -> None:
        self._parser = parser
        self._movie = movie_processor
        self._tv = tv_processor

    def format_file(self, filepath: str) -> bool | None:
        ctx = self._parser.parse(filepath)
        if ctx.skip_reason:
            logger.info(f"Skipped {os.path.basename(filepath)}: {ctx.skip_reason}")
            return None
        ctx.tokens["title"] = Transliterator.transliterate_text(ctx.tokens.get("title", ""))
        if ctx.media_type == MediaType.TV:
            return self._tv.process(ctx)
        return self._movie.process(ctx)

    def format_directory(self, dirpath: str) -> bool:
        dir_name = os.path.basename(dirpath)

        # Parse directory name through the pipeline to extract season and title
        dir_ctx = self._parser.parse(dir_name)
        dir_season = dir_ctx.tokens.get("season")
        dir_title = dir_ctx.tokens.get("title", "")

        results = []
        for root, _, files in os.walk(dirpath):
            for file in files:
                if is_video_file(file):
                    filepath = os.path.join(root, file)
                    tokens = {"season": dir_season} if dir_season else {}
                    seed = ParseContext(filepath=filepath, tokens=tokens)
                    ctx = self._parser.parse(filepath, seed=seed)
                    if ctx.skip_reason:
                        logger.info(f"Skipped {file}: {ctx.skip_reason}")
                        continue
                    # Fall back to directory-derived title when file has none
                    if not ctx.tokens.get("title") and dir_title:
                        ctx.tokens["title"] = Transliterator.transliterate_text(dir_title)
                    else:
                        ctx.tokens["title"] = Transliterator.transliterate_text(ctx.tokens.get("title", ""))
                    results.append(self._tv.process(ctx))

        return any(results)
