import os


class FileStabilityTracker:
    """
    Tracks file size changes to detect when a file has stopped growing.

    A file is considered "stable" when its size remains unchanged across
    multiple scan cycles. This prevents processing incomplete downloads.
    """

    def __init__(self, stability_cycles: int = 2):
        """
        Initialize tracker.

        Args:
            stability_cycles: Number of consecutive unchanged-size scans before marking stable
        """
        self.stability_cycles = stability_cycles
        self.pending_files: dict[str, tuple[int, int]] = {}  # path -> (size, count)

    def is_stable(self, filepath: str) -> bool:
        """
        Check if a file is stable (size unchanged for N cycles).

        Args:
            filepath: Path to file to check

        Returns:
            True if file size has remained unchanged for stability_cycles scans
        """
        try:
            current_size = os.path.getsize(filepath)
        except OSError:
            # File deleted or inaccessible
            self.pending_files.pop(filepath, None)
            return False

        last_size, count = self.pending_files.get(filepath, (None, 0))

        if current_size == last_size:
            count += 1
        else:
            count = 0

        self.pending_files[filepath] = (current_size, count)
        return count >= self.stability_cycles

    def mark_processed(self, filepath: str) -> None:
        """
        Remove a file from tracking after processing.

        Args:
            filepath: Path to file to remove
        """
        self.pending_files.pop(filepath, None)

    def clear(self) -> None:
        """Clear all pending file tracking"""
        self.pending_files.clear()
