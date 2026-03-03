import os

from loguru import logger

from ..config import config
from ..metadata import TMDBClient
from ..parser import ParseContext
from ..utils.fs.file_ops import link_file
from ..utils.token_formatter import format_tokens
from .result import MediaKind, ProcessResult


class TvProcessor:
    def __init__(self, tmdb_client: TMDBClient) -> None:
        self._tmdb = tmdb_client

    def process(self, ctx: ParseContext) -> ProcessResult:
        title = ctx.tokens.get("title", "")
        year = ctx.tokens.get("year")

        tmdb_id, year = self._tmdb.search_tv(title, year)
        if tmdb_id:
            ctx.tokens["tmdb_id"] = str(tmdb_id)
        if year:
            ctx.tokens["year"] = year

        # Avoid year == title for numeric TV shows (e.g., "1923")
        if title == year:
            ctx.tokens.pop("year", None)

        tv_dir = format_tokens(config.FORMAT_TV_FOLDER, ctx.tokens)
        season_dir = format_tokens(config.FORMAT_TV_SEASON_FOLDER, ctx.tokens)
        filename = format_tokens(config.FORMAT_TV_FILE, ctx.tokens) + ctx.extension

        dest = os.path.join(config.TV_DIR, tv_dir, season_dir, filename)

        logger.info(f"TV: {title} -> {filename}")
        success = link_file(ctx.filepath, dest, dry_run=config.DRY_RUN)
        return ProcessResult(
            source=os.path.basename(ctx.filepath),
            dest=filename,
            media_kind=MediaKind.TV,
            success=success,
        )
