import os
from pathlib import Path

from loguru import logger

VIDEO_EXTENSIONS = (".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".m4v", ".ts", ".m2ts")


def is_video_file(filename: str) -> bool:
    return filename.lower().endswith(VIDEO_EXTENSIONS)


def ensure_dir(directory: str, dry_run: bool = False) -> bool:
    if os.path.exists(directory):
        return True

    if dry_run:
        logger.info(f"DRY RUN - Would create directory: {directory}")
        return True

    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")
        return True
    except PermissionError as e:
        logger.error(f"Permission denied creating directory {directory}: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        return False


def link_file(source_file: str, dest_file: str, dry_run: bool = False) -> bool:
    if not os.path.exists(source_file):
        logger.error(f"Source file does not exist: {source_file}")
        return False

    dest_dir = os.path.dirname(dest_file)
    if dest_dir and not ensure_dir(dest_dir, dry_run=dry_run):
        return False

    if dry_run:
        logger.info(f"DRY RUN - Would link: {source_file} -> {dest_file}")
        return True

    if os.path.exists(dest_file):
        logger.warning(f"Destination file already exists: {dest_file}")
        try:
            os.remove(dest_file)
            logger.info(f"Removed existing destination file: {dest_file}")
        except Exception as e:
            logger.error(f"Cannot remove {dest_file}: {e}")
            return False

    try:
        os.link(source_file, dest_file)
        logger.info(f"LINKED: {source_file} -> {dest_file}")
        return True
    except PermissionError as e:
        logger.error(f"ERROR LINKING (permission denied): {source_file} -> {dest_file} ({e})")
        return False
    except OSError as e:
        logger.error(f"ERROR LINKING (os error): {source_file} -> {dest_file} ({e})")
        return False
