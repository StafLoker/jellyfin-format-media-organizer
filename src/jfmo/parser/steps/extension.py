import os

from ..context import ParseContext

_VIDEO_EXTENSIONS = frozenset((".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".m4v", ".ts", ".m2ts"))


class ExtensionStep:
    def process(self, ctx: ParseContext) -> ParseContext:
        stem, ext = os.path.splitext(ctx.working_name)  # .mkv, .mp4, .avi, ...
        if ext.lower() in _VIDEO_EXTENSIONS:
            ctx.extension = ext
            ctx.working_name = stem
        return ctx
