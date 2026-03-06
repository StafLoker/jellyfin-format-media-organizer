import os
from datetime import datetime
from threading import Event

from loguru import logger

from .formatter import Formatter
from .utils.fs.file_ops import is_video_file
from .utils.fs.file_stability_tracker import FileStabilityTracker


class FileWatcher:
    def __init__(self, watch_dir: str, check_interval: int, formatter: Formatter) -> None:
        self.watch_dir = watch_dir
        self.check_interval = check_interval
        self.formatter = formatter
        self.known_entries: set[str] = set()
        self.pending_entries: set[str] = set()
        self.stability_tracker = FileStabilityTracker(stability_cycles=2)
        self.stop_event = Event()
        self._cycle = 0

    def _scan_entries(self) -> set[str]:
        """Return direct children of watch_dir (dirs and video files)."""
        found: set[str] = set()
        try:
            for name in os.listdir(self.watch_dir):
                path = os.path.join(self.watch_dir, name)
                if os.path.isdir(path) or (os.path.isfile(path) and is_video_file(name)):
                    found.add(path)
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")
        return found

    def _is_stable(self, path: str) -> bool:
        """Check stability: for dirs, check all video files inside are stable."""
        if os.path.isfile(path):
            return self.stability_tracker.is_stable(path)
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                if is_video_file(filename) and not self.stability_tracker.is_stable(os.path.join(root, filename)):
                    return False
        return True

    def _mark_processed(self, path: str) -> None:
        if os.path.isfile(path):
            self.stability_tracker.mark_processed(path)
        else:
            for root, _, filenames in os.walk(path):
                for filename in filenames:
                    if is_video_file(filename):
                        self.stability_tracker.mark_processed(os.path.join(root, filename))

    def _ts(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _process_pending_entry(self, path: str) -> bool:
        name = os.path.basename(path)

        if not self._is_stable(path):
            return False

        self._mark_processed(path)
        logger.info(f"New entry: {name}")

        try:
            result = self.formatter.format_directory(path) if os.path.isdir(path) else self.formatter.format_file(path)

            if result is None:
                logger.info(f"Skipped: {name}")
            elif result:
                logger.info(f"Processed: {name}")
            else:
                logger.error(f"Failed: {name}")
        except Exception as e:
            logger.error(f"Error processing {name}: {e}")

        return True

    def start(self) -> None:
        self.known_entries = self._scan_entries()
        logger.info(f"Watching {len(self.known_entries)} existing entries")

        while not self.stop_event.is_set():
            try:
                current_entries = self._scan_entries()
                new_entries = current_entries - self.known_entries

                self.pending_entries.update(new_entries)

                # Keep only entries still on disk; process the stable ones
                self.pending_entries &= current_entries
                for path in list(self.pending_entries):
                    if self._process_pending_entry(path):
                        self.pending_entries.discard(path)
                        self.known_entries.add(path)

                # Drop known entries that disappeared from disk
                self.known_entries &= current_entries
                self._cycle += 1

                if self._cycle % 10 == 0:
                    logger.info(f"[{self._ts()}] watching {len(current_entries)} entries")

                self.stop_event.wait(self.check_interval)

            except KeyboardInterrupt:
                logger.info("Interrupted")
                break
            except Exception as e:
                logger.error(f"Watch loop error: {e}")
                self.stop_event.wait(self.check_interval)

    def stop(self) -> None:
        self.stop_event.set()
