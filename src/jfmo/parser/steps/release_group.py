import re

from ..context import ParseContext
from ..tokens import Token

_RELEASE_GROUP = re.compile(r"-([A-Za-z][A-Za-z0-9]+)$")  # trailing -GroupName


class ReleaseGroupStep:
    def process(self, ctx: ParseContext) -> ParseContext:
        match = _RELEASE_GROUP.search(ctx.working_name.strip())
        if match:
            ctx.tokens[Token.RELEASE_GROUP] = match.group(1)
            ctx.working_name = _RELEASE_GROUP.sub("", ctx.working_name.strip())
        return ctx
