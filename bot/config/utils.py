from os import environ

from .default import DefaultSettings
from .production import ProductionSettings


def get_settings() -> DefaultSettings:  # pragma: no cover
    env = environ.get('ENV', 'local')
    if env == 'local':
        return DefaultSettings()  # type: ignore[call-arg]
    if env == 'production':
        return ProductionSettings()  # type: ignore[call-arg]
    # ...
    # space for other settings
    # ...
    return DefaultSettings()  # type: ignore[call-arg]  # fallback to default
