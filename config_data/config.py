import os
from dotenv import load_dotenv, find_dotenv


def setup_parameters() -> tuple[str, str, str, int, str]:
    """
    Загружает параметры из файла .env и возвращает их в виде кортежа.
    Если файл .env не найдет, то выводит соответствующее сообщение.

    Returns:
        tuple: Токен доступа, локальная директория, облачная директория,
               интервал синхронизации (в секундах) и имя файла лога.
    Raises:
         EnvironmentError: Если обязательные переменные окружения отсутствуют.
    """
    if not find_dotenv():
        exit("Переменные окружения не загружены т.к отсутствует файл .env")
    else:
        load_dotenv()  # Загружаем переменные окружения из .env файла

    required_vars = ["TOKEN", "LOCAL_DIR", "CLOUD_DIR"]

    for var in required_vars:
        if os.getenv(var) is None:
            raise EnvironmentError(f"Отсутствует обязательная переменная окружения: {var}")

    token = os.getenv("TOKEN")
    local_dir = os.getenv("LOCAL_DIR")
    cloud_dir = os.getenv("CLOUD_DIR")
    sync_interval = int(os.getenv("SYNC_INTERVAL", 60)) # По умолчанию 60 секунд
    log_file = os.getenv("LOG_FILE", "sync_service.log") # По умолчанию sync_service.log

    return token, local_dir, cloud_dir, sync_interval, log_file