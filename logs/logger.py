from loguru import logger


def setup_logger(log_file: str) -> logger:
    """
    Настраивает логгер для записи логов в указанный файл.

    Args:
        log_file (str): Путь к файлу для записи логов.
    Returns:
        logger: Настроенный логгер.
    """
    logger.add(log_file, format="{time} {level} {message}", level="INFO")

    return logger