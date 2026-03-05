from unittest.mock import MagicMock

import pytest

from jfmo.daemon import FileWatcher


class TestFileWatcher:
    @pytest.fixture()
    def watch_dir(self, tmp_path):
        d = tmp_path / "watch"
        d.mkdir()
        return d

    @pytest.fixture()
    def formatter(self):
        return MagicMock()

    def _make_watcher(self, watch_dir, formatter, check_interval=1):
        return FileWatcher(str(watch_dir), check_interval, formatter)

    def test_scan_finds_video_files(self, watch_dir, formatter):
        (watch_dir / "movie.mkv").write_bytes(b"data")
        watcher = self._make_watcher(watch_dir, formatter)
        entries = watcher._scan_entries()
        assert len(entries) == 1

    def test_scan_finds_directories(self, watch_dir, formatter):
        (watch_dir / "Some.Show.S01E01").mkdir()
        watcher = self._make_watcher(watch_dir, formatter)
        entries = watcher._scan_entries()
        assert len(entries) == 1

    def test_scan_ignores_non_video_files(self, watch_dir, formatter):
        (watch_dir / "readme.txt").write_text("hello")
        (watch_dir / "image.jpg").write_bytes(b"\xff")
        watcher = self._make_watcher(watch_dir, formatter)
        entries = watcher._scan_entries()
        assert len(entries) == 0

    def test_new_stable_file_gets_processed(self, watch_dir, formatter):
        """A file that is already stable should be processed."""
        watcher = self._make_watcher(watch_dir, formatter)
        watcher.known_entries = set()

        video = watch_dir / "movie.mkv"
        video.write_bytes(b"data")
        video_path = str(video)

        # Pre-stabilize the file in the tracker
        watcher.stability_tracker.is_stable(video_path)
        watcher.stability_tracker.is_stable(video_path)
        watcher.stability_tracker.is_stable(video_path)

        watcher._process_pending_entry(video_path)
        formatter.format_file.assert_called_once_with(video_path)

    def test_new_unstable_file_not_processed(self, watch_dir, formatter):
        """A file that just appeared should NOT be processed (not stable yet)."""
        watcher = self._make_watcher(watch_dir, formatter)
        video = watch_dir / "movie.mkv"
        video.write_bytes(b"data")

        watcher._process_pending_entry(str(video))
        formatter.format_file.assert_not_called()

    def test_unstable_entry_eventually_processed_across_cycles(self, watch_dir, formatter):
        """
        A new entry that is not yet stable should eventually be
        processed once it becomes stable in subsequent watch cycles.
        """
        formatter.format_file.return_value = True
        watcher = self._make_watcher(watch_dir, formatter, check_interval=0)

        # Start with empty watch dir
        watcher.known_entries = watcher._scan_entries()
        assert len(watcher.known_entries) == 0

        # A new video file appears
        video = watch_dir / "movie.mkv"
        video.write_bytes(b"data")

        # Simulate multiple watch cycles using the same logic as start()
        cycles_run = 0
        max_cycles = 10

        while cycles_run < max_cycles:
            current_entries = watcher._scan_entries()
            new_entries = current_entries - watcher.known_entries

            watcher.pending_entries.update(new_entries)

            watcher.pending_entries &= current_entries
            for path in list(watcher.pending_entries):
                if watcher._process_pending_entry(path):
                    watcher.pending_entries.discard(path)
                    watcher.known_entries.add(path)

            watcher.known_entries &= current_entries
            cycles_run += 1

            if formatter.format_file.called:
                break

        assert formatter.format_file.called, f"File was never processed after {cycles_run} cycles."

    def test_directory_entry_eventually_processed(self, watch_dir, formatter):
        """Same bug but for directory entries."""
        formatter.format_directory.return_value = True
        watcher = self._make_watcher(watch_dir, formatter, check_interval=0)

        watcher.known_entries = watcher._scan_entries()

        # A new directory with a video file appears
        show_dir = watch_dir / "Some.Show.S01E01"
        show_dir.mkdir()
        (show_dir / "episode.mkv").write_bytes(b"data")

        cycles_run = 0
        max_cycles = 10

        while cycles_run < max_cycles:
            current_entries = watcher._scan_entries()
            new_entries = current_entries - watcher.known_entries

            watcher.pending_entries.update(new_entries)

            watcher.pending_entries &= current_entries
            for path in list(watcher.pending_entries):
                if watcher._process_pending_entry(path):
                    watcher.pending_entries.discard(path)
                    watcher.known_entries.add(path)

            watcher.known_entries &= current_entries
            cycles_run += 1

            if formatter.format_directory.called:
                break

        assert formatter.format_directory.called, f"Directory was never processed after {cycles_run} cycles."
