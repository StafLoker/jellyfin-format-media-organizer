import re

from ..context import MediaType, ParseContext

_DEFINITIVE_TV_PATTERNS = [
    re.compile(r"S[0-9]{1,2}E[0-9]{1,2}", re.IGNORECASE),  # S01E01
    re.compile(r"S[0-9]{1,2}\.E[0-9]{1,2}", re.IGNORECASE),  # S01.E01
    re.compile(r"\bs[0-9]{1,2}e[0-9]{1,2}\b"),  # s01e01 (word boundary)
    re.compile(r"S[0-9]{1,2}E[0-9]{1,2}-E?[0-9]{1,2}", re.IGNORECASE),  # S01E01-E02, S01E01-02
    re.compile(r"[0-9]{1,2}[xX][0-9]{1,2}"),  # 3x07, 3X07
]

_AMBIGUOUS_PATTERNS = [
    (re.compile(r"[Ee]pisode[. ]([0-9]{1,2})", re.IGNORECASE), "Episode X format"),  # Episode 3
    (re.compile(r"(?<![0-9])([0-9]{1})([0-9]{2})(?![0-9])"), "Combined season/episode (NNN)"),  # 308 → S03E08
    (re.compile(r"(19|20)[0-9]{2}[.-][0-9]{2}[.-][0-9]{2}"), "Date-based format"),  # 2024.01.15
]

_MOVIE_WITH_QUALITY = re.compile(  # year + quality → likely movie, not episode
    r"(19|20)[0-9]{2}.*\b(720|1080|2160)p\b", re.IGNORECASE
)


def _has_definitive_tv(name: str) -> bool:
    return any(p.search(name) for p in _DEFINITIVE_TV_PATTERNS)


def _is_ambiguous(name: str) -> tuple[bool, str]:
    if _has_definitive_tv(name):
        return False, ""
    for pattern, reason in _AMBIGUOUS_PATTERNS:
        if pattern.search(name):
            if pattern is _AMBIGUOUS_PATTERNS[1][0] and _MOVIE_WITH_QUALITY.search(name):
                continue
            return True, reason
    return False, ""


class MediaTypeStep:
    def process(self, ctx: ParseContext) -> ParseContext:
        # Use original filepath basename for pattern matching (working_name is already stripped)
        original = ctx.filepath.rsplit("/", 1)[-1] if "/" in ctx.filepath else ctx.filepath

        ambiguous, reason = _is_ambiguous(original)
        if ambiguous:
            ctx.skip_reason = f"ambiguous pattern: {reason}"
            ctx.media_type = MediaType.AMBIGUOUS
        elif "season" in ctx.tokens or "episode" in ctx.tokens or _has_definitive_tv(original):
            ctx.media_type = MediaType.TV
        else:
            ctx.media_type = MediaType.MOVIE
        return ctx
