import logging
import pathlib
import sys

import loguru

from bot import config

from . import custom_loki_logger_handler


LABEL_KEYS = {
    'function',
    'name',
    'level',
    'tg_command',
    'log_type',
}
LOGGER_PARAMS = {
    'rotation': '128 MB',
    'retention': 10,
    'compression': 'tar.gz',
    'serialize': True,
    'enqueue': True,
}


def configure_logger(
    settings: config.DefaultSettings,
    log_file: pathlib.Path,
    application: str,
) -> None:  # pragma: no cover
    loguru.logger.remove()
    loguru.logger.add(sink=sys.stderr, serialize=not settings.DEBUG, enqueue=True)
    loguru.logger.add(
        log_file,
        **LOGGER_PARAMS,  # type: ignore
    )
    loguru.logger.add(
        sink=custom_loki_logger_handler.CustomLokiLoggerHandler(
            url=settings.LOKI_PUSH_URL,
            labels={
                'application': application,
                'environment': settings.ENV,
                'log_type': 'log',  # default
            },
            label_keys=LABEL_KEYS,
            timeout=10,
            default_formatter=custom_loki_logger_handler.CustomLoguruFormatter(),
        ),
        serialize=True,
    )
    logging.getLogger('sqlalchemy.engine').setLevel('INFO')
