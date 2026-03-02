class DirectoryNotFoundError(Exception):
    """Raised when a required media directory does not exist."""


class DaemonError(Exception):
    """Raised when the daemon fails to start."""


class TransliterationModelError(Exception):
    """Raised when language models cannot be loaded."""
