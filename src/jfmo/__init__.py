import os
import signal
import sys

from loguru import logger

from .cli import CLI
from .config import config
from .daemon import FileWatcher
from .di import Container
from .exceptions import DirectoryNotFoundError, TransliterationModelError
from .utils.fs.file_ops import is_video_file

EXIT_SUCCESS = 0
EXIT_CONFIG_ERROR = 1
EXIT_DIRECTORY_ERROR = 2
EXIT_SYSTEM_ERROR = 5
EXIT_MODEL_ERROR = 6


def _run(apply: bool) -> None:
    config.DRY_RUN = not apply
    container = Container()

    for name in os.listdir(config.DOWNLOADS_DIR):
        path = os.path.join(config.DOWNLOADS_DIR, name)

        if os.path.isdir(path):
            container.formatter.format_directory(path)
        elif os.path.isfile(path) and is_video_file(name):
            container.formatter.format_file(path)


def _run_daemon() -> None:
    config.DAEMON_MODE = True
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
