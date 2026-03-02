import os

from .context import ParseContext
from .protocol import ParsingStep


class Parser:
    def __init__(self, *steps: ParsingStep) -> None:
        self._steps = steps

    def parse(self, filepath: str, seed: ParseContext | None = None) -> ParseContext:
        ctx = seed if seed is not None else ParseContext(filepath=filepath)
        if not ctx.working_name:
            ctx.working_name = os.path.basename(ctx.filepath)
        for step in self._steps:
            ctx = step.process(ctx)
            if ctx.skip_reason:
                break
        return ctx
