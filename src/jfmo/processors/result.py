from dataclasses import dataclass
from enum import Enum


class MediaKind(Enum):
    MOVIE = "Movie"
    TV = "TV"


@dataclass(frozen=True)
class ProcessResult:
    source: str  # basename of source file
    dest: str  # basename of destination file
    media_kind: MediaKind
    success: bool  # True = linked (or would-link in dry-run)
