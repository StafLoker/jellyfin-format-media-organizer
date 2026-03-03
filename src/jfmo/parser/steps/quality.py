import re

from ..context import ParseContext
from ..tokens import Token

_STANDARD = re.compile(r"(480|720|1080|2160|4320)p", re.IGNORECASE)  # 720p, 1080p, 2160p, 4320p
_CYRILLIC_P = re.compile(r"(240|352|480|576|720|1080|2160|4320)р")  # 1080р (Cyrillic р)

_RESOLUTION_MAP = [
    (re.compile(r"1920\s*[xX]\s*1080"), "1080p"),  # 1920x1080
    (re.compile(r"1280\s*[xX]\s*720"), "720p"),  # 1280x720
    (re.compile(r"3840\s*[xX]\s*2160"), "2160p"),  # 3840x2160
    (re.compile(r"7680\s*[xX]\s*4320"), "4320p"),  # 7680x4320
    (re.compile(r"720\s*[xX]\s*480"), "480p"),  # 720x480
    (re.compile(r"720\s*[xX]\s*576"), "576p"),  # 720x576
]

_HD_LABELS = [
    (re.compile(r"\bSD\b", re.IGNORECASE), "480p"),  # SD
    (re.compile(r"\bFHD\b", re.IGNORECASE), "1080p"),  # FHD
    (re.compile(r"\bQHD\b", re.IGNORECASE), "1440p"),  # QHD
    (re.compile(r"\bUHD\b|\b4K\b", re.IGNORECASE), "2160p"),  # UHD, 4K
    (re.compile(r"\b8K\b", re.IGNORECASE), "4320p"),  # 8K
    (re.compile(r"\bHD\b", re.IGNORECASE), "720p"),  # HD
]

# Strips quality marker and everything after it (residual audio tags, language codes, etc.)
_QUALITY_AND_TAIL = re.compile(
    r"\b(480|720|1080|2160|4320)[pр]\b.*"
    r"|\b(SD|HD|FHD|QHD|UHD|4K|8K)\b.*"
    r"|[0-9]{3,4}\s*[xX]\s*[0-9]{3,4}.*",
    re.IGNORECASE,
)


def _detect_quality(name: str) -> str:
    match = _STANDARD.search(name)
    if match:
        return f"[{match.group(0)}]"

    match = _CYRILLIC_P.search(name)
    if match:
        return f"[{match.group(1)}p]"

    for pattern, quality in _RESOLUTION_MAP:
        if pattern.search(name):
            return f"[{quality}]"

    for pattern, quality in _HD_LABELS:
        if pattern.search(name):
            return f"[{quality}]"

    if re.search(r"[0-9]{3,4}x[0-9]{3,4}", name, re.IGNORECASE):
        return "[custom]"

    return ""


class QualityStep:
    def process(self, ctx: ParseContext) -> ParseContext:
        quality = _detect_quality(ctx.working_name)
        if quality:
            ctx.tokens[Token.QUALITY] = quality
            ctx.working_name = _QUALITY_AND_TAIL.sub("", ctx.working_name)
        return ctx
