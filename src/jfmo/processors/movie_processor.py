import os

from loguru import logger

from ..config import config
from ..metadata import TMDBClient
from ..parser import ParseContext
from ..utils.fs.file_ops import link_file
from ..utils.token_formatter import format_tokens


class MovieProcessor:
    def __init__(self, tmdb_client: TMDBClient) -> None:
        self._tmdb = tmdb_client

    def process(self, ctx: ParseContext) -> bool:
        title = ctx.tokens.get("title", "")
        year = ctx.tokens.get("year")

        tmdb_id, year = self._tmdb.search_movie(title, year)
        if tmdb_id:
            ctx.tokens["tmdb_id"] = str(tmdb_id)
        if year:
            ctx.tokens["year"] = year

        new_name = format_tokens(config.FORMAT_MOVIE_FILE, ctx.tokens) + ctx.extension
        dest = os.path.join(config.FILMS_DIR, new_name)

        logger.info(f"Movie: {title} -> {new_name}")
        return link_file(ctx.filepath, dest, dry_run=config.DRY_RUN)
