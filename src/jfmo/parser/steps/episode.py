import re

from ..context import ParseContext
from ..tokens import Token

_EPISODE_PATTERNS = [
    re.compile(r"[Ee]([0-9]{1,2})(-[Ee]?([0-9]{1,2}))?"),  # E01, E01-E03, E01-03
    re.compile(r"[Ee]pisode[.\s-]*([0-9]{1,2})", re.IGNORECASE),  # Episode 1, Episode.01
    re.compile(r"(?:^|[.\s_-])([0-9]{1,2})\.[^.]+$"),  # 01.ext — bare number before extension
]


class EpisodeStep:
    """Extract episode number when not already set.

    Handles filenames like E05.mkv or Episode.03.mkv, as well as the
    leftover Exx markers from SeasonStep.
    """

    def process(self, ctx: ParseContext) -> ParseContext:
        for pattern in _EPISODE_PATTERNS:
            match = pattern.search(ctx.working_name)
            if match:
                ctx.tokens[Token.EPISODE] = f"{int(match.group(1)):02d}"
                ctx.working_name = pattern.sub("", ctx.working_name, count=1)
                return ctx

        return ctx
