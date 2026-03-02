import pytest

from jfmo.config import config


@pytest.fixture(autouse=True)
def reset_config():
    """Restore config object attributes to their defaults after every test."""
    original = {k: v for k, v in vars(config).items() if not k.startswith("_")}
    yield
    for k, v in original.items():
        setattr(config, k, v)
