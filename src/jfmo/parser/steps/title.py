import re

from ..context import ParseContext
from ..tokens import Token

_BRACKETS = re.compile(r"\[[^\]]*\]")  # [NOOBDL], [720p], [rus]
_PARENS = re.compile(r"\([^)]*\)")  # (2024), (Director's Cut)
_DATE_PATTERN = re.compile(  # 2024.01.15, 2024-01-15
    r"(19|20)[0-9]{2}[.\-][0-9]{1,2}[.\-][0-9]{1,2}"
)
_SEPARATORS = re.compile(r"[._\-]")  # dots, underscores, hyphens → space
_WHITESPACE = re.compile(r"\s+")  # collapse multiple spaces


class TitleStep:
    def process(self, ctx: ParseContext) -> ParseContext:
        name = ctx.working_name
        name = _BRACKETS.sub("", name)
        name = _PARENS.sub("", name)
        name = _DATE_PATTERN.sub("", name)
        name = _SEPARATORS.sub(" ", name)
        name = _WHITESPACE.sub(" ", name).strip()
        ctx.tokens[Token.TITLE] = name
        return ctx
