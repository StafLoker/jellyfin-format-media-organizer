import re

from ..context import ParseContext
from ..tokens import Token

_SERVICE = re.compile(
    r"\b(NF|AMZN|DSNP|HMAX|ATVP|PCOK|PMTP|iT|STAN|CRAV|MA)\b",
)  # Netflix, Amazon, Disney+, HBO Max, Apple TV+, Peacock, Paramount+, iTunes, Stan, Crave, Movies Anywhere


class ServiceStep:
    def process(self, ctx: ParseContext) -> ParseContext:
        match = _SERVICE.search(ctx.working_name)
        if match:
            ctx.tokens[Token.SERVICE] = match.group(1)
            ctx.working_name = _SERVICE.sub("", ctx.working_name, count=1)
        return ctx
