import re

from ..context import ParseContext

_EPISODE_PATTERNS = [
    re.compile(r"[Ee]([0-9]{1,2})"),  # E01, e1
    re.compile(r"[Ee]pisode[.\s-]*([0-9]{1,2})", re.IGNORECASE),  # Episode 1, Episode.01
    re.compile(r"([0-9]{1,2})\.[^.]+$"),  # 01.mkv (number before extension)
]


class EpisodeStep:
    """Extract episode number when season is already known but episode is not.

    Handles filenames like E05.mkv or Episode.03.mkv inside a season directory.
    Only runs when season is present in tokens but episode is missing — the
    combined SxxExx case is already handled by SeasonStep.
    """

    def process(self, ctx: ParseContext) -> ParseContext:
        if "season" not in ctx.tokens or "episode" in ctx.tokens:
            return ctx

        for pattern in _EPISODE_PATTERNS:
            match = pattern.search(ctx.working_name)
            if match:
                ctx.tokens["episode"] = f"{int(match.group(1)):02d}"
                ctx.working_name = pattern.sub("", ctx.working_name)
                return ctx

        return ctx
