import logging
from app.Parser import YamlParser, EnvironmentParser
from pathlib import Path


def __get_project_root() -> str:
    return str(Path(__file__).parent.parent)


def __init_logger() -> logging.Logger:
    logger = logging.getLogger('App Logger')

    if env.DEBUG.lower() in ("true", "1"):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s | %(name)s - %(levelname)s |\t\t%(message)s (%(filename)s, row: %(lineno)d)")

    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


__BASE_DIR__ = __get_project_root()

env = EnvironmentParser(__BASE_DIR__ + "/.env")
config = YamlParser(__BASE_DIR__ + "/config/")
log = __init_logger()

# Export only necessary items
__all__ = ["__BASE_DIR__", "env", "config", "log"]
