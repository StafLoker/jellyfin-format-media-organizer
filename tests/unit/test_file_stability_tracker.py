from jfmo.utils.fs.file_stability_tracker import FileStabilityTracker


class TestFileStabilityTracker:
    def test_new_file_not_stable_on_first_check(self, tmp_path):
        tracker = FileStabilityTracker(stability_cycles=2)
        f = tmp_path / "video.mkv"
        f.write_bytes(b"x" * 100)
        assert tracker.is_stable(str(f)) is False

    def test_file_stable_after_enough_cycles(self, tmp_path):
        tracker = FileStabilityTracker(stability_cycles=2)
        f = tmp_path / "video.mkv"
        f.write_bytes(b"x" * 100)

        # cycle 0: first seen -> count=0
        assert tracker.is_stable(str(f)) is False
        # cycle 1: same size -> count=1
        assert tracker.is_stable(str(f)) is False
        # cycle 2: same size -> count=2 >= 2
        assert tracker.is_stable(str(f)) is True

    def test_file_size_change_resets_count(self, tmp_path):
        tracker = FileStabilityTracker(stability_cycles=2)
        f = tmp_path / "video.mkv"
        f.write_bytes(b"x" * 100)

        tracker.is_stable(str(f))  # count=0
        tracker.is_stable(str(f))  # count=1

        # size changes — simulating ongoing download
        f.write_bytes(b"x" * 200)
        assert tracker.is_stable(str(f)) is False  # count reset to 0
        assert tracker.is_stable(str(f)) is False  # count=1
        assert tracker.is_stable(str(f)) is True  # count=2

    def test_deleted_file_not_stable(self, tmp_path):
        tracker = FileStabilityTracker(stability_cycles=2)
        f = tmp_path / "video.mkv"
        f.write_bytes(b"x" * 100)
        tracker.is_stable(str(f))
        f.unlink()
        assert tracker.is_stable(str(f)) is False

    def test_mark_processed_removes_tracking(self, tmp_path):
        tracker = FileStabilityTracker(stability_cycles=2)
        f = tmp_path / "video.mkv"
        f.write_bytes(b"x" * 100)
        tracker.is_stable(str(f))
        tracker.mark_processed(str(f))
        assert str(f) not in tracker.pending_files
