import re

from ..context import ParseContext

# Full season+episode patterns (ordered by specificity)
_SEASON_EPISODE_PATTERNS = [
    re.compile(r"[Ss]([0-9]{1,2})[Ee]([0-9]{1,2})-[Ee]?[0-9]{1,2}"),  # S01E01-E02, S01E01-02
    re.compile(r"[Ss]([0-9]{1,2})\.?[Ee]([0-9]{1,2})"),  # S01E01, S01.E01, s01e01
    re.compile(r"(?<![0-9])([0-9]{1,2})[xX]([0-9]{1,2})(?![0-9])"),  # 3x07, 3X07
]

# Removal patterns — strip the full SxxExx token from working_name
_REMOVE_PATTERNS = [
    re.compile(r"[Ss][0-9]{1,2}\.?[Ee][0-9]{1,2}(-[Ee]?[0-9]{1,2})?"),  # S01E01, S01.E01, S01E01-E02
    re.compile(r"(?<![0-9])[0-9]{1,2}[xX][0-9]{1,2}(?![0-9])"),  # 3x07
]

_SEASON_ONLY = re.compile(r"\b[Ss]([0-9]{1,2})\b")  # S01, s1 — standalone season


class SeasonStep:
    """Extract season (and co-located episode) from combined SxxExx patterns.

    When the filename contains SxxExx or NxNN, both season and episode are
    extracted because they are inseparable in the pattern. Standalone season
    patterns (S02 without episode) are also handled.
    """

    def process(self, ctx: ParseContext) -> ParseContext:
        for pattern in _SEASON_EPISODE_PATTERNS:
            match = pattern.search(ctx.working_name)
            if match:
                ctx.tokens["season"] = f"{int(match.group(1)):02d}"
                ctx.tokens["episode"] = f"{int(match.group(2)):02d}"
                for rp in _REMOVE_PATTERNS:
                    ctx.working_name = rp.sub("", ctx.working_name)
                return ctx

        # Standalone season (e.g. directory name "Breaking.Bad.S02")
        if "season" not in ctx.tokens:
            match = _SEASON_ONLY.search(ctx.working_name)
            if match:
                ctx.tokens["season"] = f"{int(match.group(1)):02d}"
                ctx.working_name = _SEASON_ONLY.sub("", ctx.working_name)

        return ctx
