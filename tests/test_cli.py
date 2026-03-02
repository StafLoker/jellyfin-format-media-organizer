import sys

from jfmo.cli import CLI


def _cli(*args):
    """Helper: create a CLI instance with the given args."""
    sys.argv = ["jfmo"] + list(args)
    return CLI()


# ---------------------------------------------------------------------------
# run subcommand
# ---------------------------------------------------------------------------


def test_run_default_is_dry_run():
    cli = _cli("run")
    assert cli.read_command() == "run"
    assert cli.read_run_apply() is False


def test_run_apply_flag():
    cli = _cli("run", "--apply")
    assert cli.read_run_apply() is True


def test_run_short_apply_flag():
    cli = _cli("run", "-a")
    assert cli.read_run_apply() is True


def test_run_custom_config():
    cli = _cli("-c", "/etc/jfmo/custom.yaml", "run")
    assert cli.read_config_path() == "/etc/jfmo/custom.yaml"


# ---------------------------------------------------------------------------
# daemon subcommand
# ---------------------------------------------------------------------------


def test_daemon_defaults():
    cli = _cli("daemon")
    assert cli.read_command() == "daemon"


def test_daemon_custom_config():
    cli = _cli("-c", "/home/user/jfmo.yaml", "daemon")
    assert cli.read_config_path() == "/home/user/jfmo.yaml"


# ---------------------------------------------------------------------------
# no subcommand
# ---------------------------------------------------------------------------


def test_no_subcommand_returns_none():
    cli = _cli()
    assert cli.read_command() is None


def test_default_config_path():
    cli = _cli("run")
    assert cli.read_config_path() == "/etc/jfmo/config.yaml"
