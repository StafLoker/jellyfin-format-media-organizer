import re

from ..context import ParseContext
from ..tokens import Token

# Season+episode patterns — extract only season, leave episode marker for EpisodeStep
_SEASON_EPISODE_PATTERNS = [
    (
        re.compile(r"[Ss]([0-9]{1,2})[Ee]([0-9]{1,2})-[Ee]?([0-9]{1,2})"),  # S01E01-E03, S01E01-03
        lambda m: f"E{m.group(2)}-E{m.group(3)}",  # → E01-E03
    ),
    (
        re.compile(r"[Ss]([0-9]{1,2})\.?[Ee]([0-9]{1,2})"),  # S01E05, S01.E01, s01e01
        lambda m: f"E{m.group(2)}",  # → E05
    ),
    (
        re.compile(r"(?<![0-9])([0-9]{1,2})[xX]([0-9]{1,2})(?![0-9])"),  # 3x07
        lambda m: f"E{m.group(2)}",  # → E07
    ),
]

_SEASON_ONLY = re.compile(r"\b[Ss]([0-9]{1,2})\b")  # S01, s1 — standalone season


class SeasonStep:
    """Extract season from combined SxxExx patterns.

    Replaces the full SxxExx marker with just the Exx portion so that
    EpisodeStep can pick it up downstream.
    """

    def process(self, ctx: ParseContext) -> ParseContext:
        for pattern, replacement in _SEASON_EPISODE_PATTERNS:
            match = pattern.search(ctx.working_name)
            if match:
                ctx.tokens[Token.SEASON] = f"{int(match.group(1)):02d}"
                ctx.working_name = pattern.sub(replacement(match), ctx.working_name, count=1)
                return ctx

        # Standalone season (e.g. directory name "Breaking.Bad.S02")
        if Token.SEASON not in ctx.tokens:
            match = _SEASON_ONLY.search(ctx.working_name)
            if match:
                ctx.tokens[Token.SEASON] = f"{int(match.group(1)):02d}"
                ctx.working_name = _SEASON_ONLY.sub("", ctx.working_name)

        return ctx
