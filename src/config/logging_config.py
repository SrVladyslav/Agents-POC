import logging

from src.config.settings import Environment, secrets

_LEVEL_BY_ENVIRONMENT: dict[Environment, int] = {
    Environment.DEV: logging.DEBUG,
    Environment.STAGING: logging.INFO,
    Environment.PROD: logging.INFO,
}


def configure_logging() -> None:
    """Configures the root logger once for the whole process.

    The log level is derived from `secrets.environment`: DEV logs at DEBUG,
    STAGING/PROD log at INFO. Call this once, as early as possible (e.g. at
    the top of `main()`), before any module logs anything.
    """
    level = _LEVEL_BY_ENVIRONMENT[secrets.environment]

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
