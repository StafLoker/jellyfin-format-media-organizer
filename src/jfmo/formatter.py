import os

from loguru import logger

from .parser import MediaType, ParseContext, Parser
from .processors.movie_processor import MovieProcessor
from .processors.result import ProcessResult
from .processors.tv_processor import TvProcessor
from .transliteration import Transliterator
from .utils.fs.file_ops import is_video_file


class Formatter:
    def __init__(self, parser: Parser, movie_processor: MovieProcessor, tv_processor: TvProcessor) -> None:
        self._parser = parser
        self._movie = movie_processor
        self._tv = tv_processor

    def format_file(self, filepath: str) -> ProcessResult | None:
        ctx = self._parser.parse(filepath)
        if ctx.skip_reason:
            logger.info(f"Skipped {os.path.basename(filepath)}: {ctx.skip_reason}")
            return None
        ctx.tokens["title"] = Transliterator.transliterate_text(ctx.tokens.get("title", ""))
        if ctx.media_type == MediaType.TV:
            return self._tv.process(ctx)
        return self._movie.process(ctx)

    def format_directory(self, dirpath: str) -> list[ProcessResult]:
        root_ctx = self._parser.parse(os.path.basename(dirpath))
        root_season = root_ctx.tokens.get("season")
        root_title = root_ctx.tokens.get("title", "")

        results: list[ProcessResult] = []
        for current_dir, _, files in os.walk(dirpath):
            # Determine season: filename > subdirectory > root dir > None
            if current_dir == dirpath:
                effective_season = root_season
            else:
                sub_ctx = self._parser.parse(os.path.basename(current_dir))
                effective_season = sub_ctx.tokens.get("season") or root_season

            for file in files:
                if is_video_file(file):
                    filepath = os.path.join(current_dir, file)
                    tokens = {"season": effective_season} if effective_season else {}
                    seed = ParseContext(filepath=filepath, tokens=tokens)
                    ctx = self._parser.parse(filepath, seed=seed)
                    if ctx.skip_reason:
                        logger.info(f"Skipped {file}: {ctx.skip_reason}")
                        continue
                    if not ctx.tokens.get("title") and root_title:
                        ctx.tokens["title"] = Transliterator.transliterate_text(root_title)
                    else:
                        ctx.tokens["title"] = Transliterator.transliterate_text(ctx.tokens.get("title", ""))
                    results.append(self._tv.process(ctx))

        return results
