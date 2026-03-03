from dataclasses import dataclass, field
from enum import Enum


class MediaType(Enum):
    MOVIE = "movie"
    TV = "tv"
    AMBIGUOUS = "ambiguous"
    UNKNOWN = "unknown"


@dataclass
class ParseContext:
    filepath: str
    working_name: str = ""
    extension: str = ""
    tokens: dict[str, str] = field(default_factory=dict)
    media_type: MediaType = MediaType.UNKNOWN
    skip_reason: str | None = None
