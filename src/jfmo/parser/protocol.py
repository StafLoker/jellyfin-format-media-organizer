from typing import Protocol

from .context import ParseContext


class ParsingStep(Protocol):
    def process(self, ctx: ParseContext) -> ParseContext: ...
