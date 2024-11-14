from time import sleep

from config_data.config import setup_parameters
from logs.logger import setup_logger
from cloud_connector.yandex_disk_connector import YandexDiskConnector
from sync_service.sync import sync_files


def main() -> None:
    """Главная функция программы, которая настраивает параметры, логгер и запускает цикл синхронизации."""

    # Настройка параметров работы
    token, local_dir, cloud_dir, sync_interval, log_file = setup_parameters()

    # Настройка логгера
    logger = setup_logger(log_file)

    # Создание объекта класса-коннектора
    connector = YandexDiskConnector(token=token, cloud_dir=cloud_dir)

    while True:
        # Синхронизация файлов
        sync_files(connector=connector, local_dir=local_dir, log=logger)
        sleep(sync_interval)


if __name__ == "__main__":
    main()