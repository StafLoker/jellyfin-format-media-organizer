import re
from datetime import datetime

from ..context import ParseContext

_YEAR_PATTERN = re.compile(r"\b(19\d{2}|20\d{2})\b")  # 1900–2099
_CURRENT_YEAR = datetime.now().year


def _detect_year(name: str) -> str:
    matches = _YEAR_PATTERN.findall(name)
    for match in matches:
        if int(match) <= _CURRENT_YEAR + 1:
            return match
    return ""


def _remove_year(name: str, year: str) -> str:
    return re.sub(rf"\b{year}\b", "", name)


class YearStep:
    def process(self, ctx: ParseContext) -> ParseContext:
        year = _detect_year(ctx.working_name)
        if year:
            ctx.tokens["year"] = year
            ctx.working_name = _remove_year(ctx.working_name, year)
        return ctx
