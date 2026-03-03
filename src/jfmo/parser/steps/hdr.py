import re

from ..context import ParseContext
from ..tokens import Token

_HDR = re.compile(
    r"\b(Dolby[.\s]?Vision|DoVi|HDR10\+|HDR10Plus|HDR10|HDR|DV|SDR)\b",
    re.IGNORECASE,
)  # Dolby Vision, DoVi, HDR10+, HDR10, HDR, DV, SDR


class HdrStep:
    def process(self, ctx: ParseContext) -> ParseContext:
        match = _HDR.search(ctx.working_name)
        if match:
            ctx.tokens[Token.HDR] = match.group(1)
            ctx.working_name = _HDR.sub("", ctx.working_name, count=1)
        return ctx
