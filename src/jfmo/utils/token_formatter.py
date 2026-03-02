import re

# Matches a delimited segment that still contains an un-substituted {token}
_BRACKETED_WITH_TOKEN = re.compile(
    r"\s*"
    r"(?:"
    r"\([^)]*\{[^}]+\}[^)]*\)"
    r"|"
    r"\[[^\]]*\{[^}]+\}[^\]]*\]"
    r")"
)

_DASH_SEGMENT_WITH_TOKEN = re.compile(
    r"\s*-\s*[^\s\-{][^\-{]*\{[^}]+\}[^\-{]*"
    r"|"
    r"\s*-\s*\{[^}]+\}"
)


def format_tokens(pattern: str, tokens: dict[str, str]) -> str:
    result = pattern

    for key, value in tokens.items():
        if value is not None and str(value) != "":
            result = result.replace(f"{{{key}}}", str(value))

    result = _BRACKETED_WITH_TOKEN.sub("", result)
    result = _DASH_SEGMENT_WITH_TOKEN.sub("", result)
    result = re.sub(r"\{[^}]+\}", "", result)

    result = re.sub(r"\s*-\s*$", "", result)
    result = re.sub(r"^\s*-\s*", "", result)
    result = re.sub(r"\s+", " ", result)
    return result.strip()
