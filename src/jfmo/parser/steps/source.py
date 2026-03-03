import re

from ..context import ParseContext
from ..tokens import Token

_SOURCE = re.compile(
    r"\b(WEB-DL|WEBDL|WEB-?Rip|WEBRip|BluRay|BDRip|BRRip|DVDRip|HDTV|PDTV|SDTV|CAM|TS|TC|SCR|R5|DVDScr)\b",
    re.IGNORECASE,
)


class SourceStep:
    def process(self, ctx: ParseContext) -> ParseContext:
        match = _SOURCE.search(ctx.working_name)
        if match:
            ctx.tokens[Token.SOURCE] = match.group(1)
            ctx.working_name = _SOURCE.sub("", ctx.working_name, count=1)
        return ctx
