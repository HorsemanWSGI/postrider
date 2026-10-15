import os
from pathlib import Path
from postrider import read_configuration
from postrider.mailer import SMTPConfiguration
from dynaconf import Dynaconf


HERE = Path(__file__).parent


def test_settings():
    settings = read_configuration(HERE / 'conf.toml')
    config = SMTPConfiguration.factory(**settings.smtp)
    assert config.port == "25"


def test_settings_envvar():
    _environ = dict(os.environ)
    try:
        os.environ['POSTRIDER_SMTP__PORT'] = "'666'"
        settings = read_configuration(HERE / 'conf.toml')
        config = SMTPConfiguration.factory(**settings.smtp)
        assert config.port == "666"
    finally:
        os.environ.clear()
        os.environ.update(_environ)
