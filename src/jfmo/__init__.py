import os
import signal
import sys

from loguru import logger

from .cli import CLI
from .config import config
from .daemon import FileWatcher
from .di import Container
from .exceptions import DirectoryNotFoundError, TransliterationModelError
from .utils.cli_output import print_dry_run_banner, print_entry_header, print_header, print_result, print_summary
from .utils.fs.file_ops import is_video_file

EXIT_SUCCESS = 0
EXIT_CONFIG_ERROR = 1
EXIT_DIRECTORY_ERROR = 2
EXIT_SYSTEM_ERROR = 5
EXIT_MODEL_ERROR = 6


def _run(apply: bool) -> None:
    config.DRY_RUN = not apply
    container = Container()

    show_output = not config.DAEMON_MODE

    video_entries = [
        name
        for name in os.listdir(config.DOWNLOADS_DIR)
        if os.path.isdir(os.path.join(config.DOWNLOADS_DIR, name))
        or (os.path.isfile(os.path.join(config.DOWNLOADS_DIR, name)) and is_video_file(name))
    ]

    if show_output and config.DRY_RUN:
        print_dry_run_banner()
    if show_output:
        print_header(len(video_entries))

    all_results = []
    skipped_count = 0

    for name in video_entries:
        path = os.path.join(config.DOWNLOADS_DIR, name)

        if show_output:
            print_entry_header(name, is_dir=os.path.isdir(path))

        if os.path.isdir(path):
            results = container.formatter.format_directory(path)
            all_results.extend(results)
            if show_output:
                for r in results:
                    print_result(r)
        else:
            result = container.formatter.format_file(path)
            if result is None:
                skipped_count += 1
            else:
                all_results.append(result)
                if show_output:
                    print_result(result)

    if show_output:
        print_summary(all_results, skipped_count, config.DRY_RUN)
        if config.DRY_RUN:
            print_dry_run_banner()


def _run_daemon() -> None:
    container = Container()
    watcher = FileWatcher(config.DOWNLOADS_DIR, config.DAEMON_INTERVAL_SEC, container.formatter)

    def _stop(signum, _frame):
        logger.info(f"Signal {signum}. Stopping...")
        watcher.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    logger.info("Daemon starting...")
    logger.info(config)
    watcher.start()


def main():
    cli = CLI()
    command = cli.read_command()

    if command is None:
        cli.print_help()
        sys.exit(EXIT_SUCCESS)

    try:
        config.DAEMON_MODE = command == "daemon"
        config.load(cli.read_config_path())

        if command == "daemon":
            _run_daemon()
        else:
            _run(cli.read_run_apply())

    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(EXIT_CONFIG_ERROR)

    except ValueError as e:
        logger.error(str(e))
        sys.exit(EXIT_CONFIG_ERROR)

    except DirectoryNotFoundError as e:
        logger.error(str(e))
        sys.exit(EXIT_DIRECTORY_ERROR)

    except TransliterationModelError as e:
        logger.error(str(e))
        sys.exit(EXIT_MODEL_ERROR)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(EXIT_SYSTEM_ERROR)

    sys.exit(EXIT_SUCCESS)
