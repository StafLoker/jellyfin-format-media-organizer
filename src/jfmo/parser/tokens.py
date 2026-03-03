from enum import StrEnum


class Token(StrEnum):
    TITLE = "title"
    YEAR = "year"
    SEASON = "season"
    EPISODE = "episode"
    QUALITY = "quality"
    TMDB_ID = "tmdb_id"
    SOURCE = "source"
    CODEC = "codec"
    HDR = "hdr"
    SERVICE = "service"
    RELEASE_GROUP = "release_group"
