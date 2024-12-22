import pathlib

import pydantic
import pydantic_settings


class DefaultSettings(pydantic_settings.BaseSettings):
    """
    Default configs for application.

    Usually, we have three environments:
    for development, testing and production.
    But in this situation, we only have
    standard settings for local development.
    """

    ENV: str = pydantic.Field('local')
    PROJECT_NAME: str = pydantic.Field('PROJECT_NAME')
    DEBUG: bool = pydantic.Field(True)

    TG_BOT_TOKEN: pydantic.SecretStr = pydantic.Field('')

    POSTGRES_DB: str = pydantic.Field('data')
    POSTGRES_HOST: str = pydantic.Field('localhost')
    POSTGRES_USER: str = pydantic.Field('pguser')
    POSTGRES_PORT: int = pydantic.Field('5432')
    POSTGRES_PASSWORD: str = pydantic.Field('pgpswd')

    LOGGING_FORMAT: str = (
        '%(filename)s %(funcName)s [%(thread)d] '
        '[LINE:%(lineno)d]# %(levelname)-8s '
        '[%(asctime)s.%(msecs)03d] %(name)s: '
        '%(message)s'
    )
    LOGGING_FILE_DIR: pathlib.Path = pathlib.Path('logs')
    LOGGING_BOT_FILE: pathlib.Path = LOGGING_FILE_DIR / 'logfile.log'
    LOGGING_WORKER_FILE: pathlib.Path = LOGGING_FILE_DIR / 'worker_logfile.log'

    BASE_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent.parent

    TG_HELPER_BOT_TOKEN: str = pydantic.Field(
        '1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234',
    )
    TG_ERROR_CHAT_ID: str = pydantic.Field('')
    TG_DB_DUMP_CHAT_ID: str = pydantic.Field('')
    TG_LOG_SEND_CHAT_ID: str = pydantic.Field('')

    LOKI_PUSH_URL: str = pydantic.Field(
        'http://loki:3100/loki/api/v1/push',
    )

    YANDEX_CLOUD_PRIVATE_KEY_FILE: str = pydantic.Field('')
    YANDEX_CLOUD_KEY_ID: str = pydantic.Field('')
    YANDEX_CLOUD_SERVICE_ACCOUNT_ID: str = pydantic.Field('')
    YANDEX_CLOUD_CATALOG_ID: str = pydantic.Field('')

    @property
    def database_settings(self) -> dict[str, str | int]:
        """
        Get all settings for connection with database.
        """
        return {
            'database': self.POSTGRES_DB,
            'user': self.POSTGRES_USER,
            'password': self.POSTGRES_PASSWORD,
            'host': self.POSTGRES_HOST,
            'port': self.POSTGRES_PORT,
        }

    @property
    def database_uri(self) -> str:
        """
        Get uri for connection with database.
        """
        return 'postgresql+asyncpg://{user}:{password}@' '{host}:{port}/{database}'.format(
            **self.database_settings,
        )

    @property
    def database_uri_sync(self) -> str:
        """
        Get uri for connection with database.
        """
        return 'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
            **self.database_settings,
        )

    model_config = pydantic_settings.SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )
