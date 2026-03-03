import re

from ..context import ParseContext
from ..tokens import Token

_CODEC = re.compile(
    r"\b(x264|x265|H\.?264|H\.?265|HEVC|AVC|VP9|AV1)\b",
    re.IGNORECASE,
)  # x264, x265, H.264, H.265, HEVC, AVC, VP9, AV1


class CodecStep:
    def process(self, ctx: ParseContext) -> ParseContext:
        match = _CODEC.search(ctx.working_name)
        if match:
            ctx.tokens[Token.CODEC] = match.group(1)
            ctx.working_name = _CODEC.sub("", ctx.working_name, count=1)
        return ctx
