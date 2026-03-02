from argparse import ArgumentParser, RawDescriptionHelpFormatter
from importlib.metadata import version


class CLI:
    def __init__(self) -> None:
        self._parser = self._create_parser()
        self._args = self._parser.parse_args()

    def _create_parser(self) -> ArgumentParser:
        parser = ArgumentParser(
            prog="jfmo",
            description="Jellyfin Format Media Organizer",
            usage="%(prog)s <command> [options]",
            formatter_class=RawDescriptionHelpFormatter,
            add_help=True,
        )
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=f"{parser.prog} {version('jfmo')}",
        )

        parser.add_argument(
            "-c",
            "--config",
            metavar="FILE",
            default="/etc/jfmo/config.yaml",
            help="Path to configuration file (default: /etc/jfmo/config.yaml)",
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Run command
        run_parser = subparsers.add_parser("run", help="Process downloads directory (default: dry-run)")
        run_parser.add_argument(
            "-a",
            "--apply",
            action="store_true",
            help="Apply changes (move files). Without this flag runs as dry-run.",
        )

        # Daemon command
        subparsers.add_parser("daemon", help="Watch downloads directory for new files")

        return parser

    def read_command(self) -> str:
        return self._args.command

    def read_config_path(self) -> str:
        return self._args.config

    def read_run_apply(self) -> bool:
        return getattr(self._args, "apply", False)

    def print_help(self) -> None:
        self._parser.print_help()
