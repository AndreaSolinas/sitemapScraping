import logging
from app.Parser import YamlParser, EnvironmentParser
from pathlib import Path


def __init_logger() -> logging.Logger:
    logger = logging.getLogger('App Logger')

    logger.setLevel(logging.DEBUG) if env.DEBUG else logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s | %(name)s - %(levelname)s |\t\t%(message)s (%(filename)s, row: %(lineno)d)")

    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # Configura il FileHandler per i messaggi di debug
    debug_log_file_path = f'{__BASE_DIR__}/log/debug.log'
    debug_file_handler = logging.FileHandler(debug_log_file_path)
    debug_file_handler.setFormatter(formatter)
    logger.addHandler(debug_file_handler)

    # Configura il FileHandler per gli errori
    error_log_file_path = f'{__BASE_DIR__}/log/error.log'
    error_file_handler = logging.FileHandler(error_log_file_path)
    error_file_handler.setLevel(logging.WARNING)
    error_file_handler.setFormatter(formatter)
    logger.addHandler(error_file_handler)

    return logger


__BASE_DIR__ = str(Path(__file__).parent.parent)

env = EnvironmentParser(__BASE_DIR__ + "/.env")
yaml_config = YamlParser(__BASE_DIR__ + "/config/")
log = __init_logger()

# Export only necessary items
__all__ = ["__BASE_DIR__", "env", "yaml_config", "log"]
