import os
import hashlib
from loguru import logger

from cloud_connector.yandex_disk_connector import YandexDiskConnector


def calculate_file_hash(path: str) -> str:
    """Вычисляет MD5-хеш файла.

    Args:
        path (str): Путь к файлу.

    Returns:
        str: Хеш файла в виде шестнадцатеричной строки.
    """
    hash_md5 = hashlib.md5()

    with open(path, "rb") as file:

        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def sync_files(connector: YandexDiskConnector, local_dir: str, log: logger) -> None:
    """
    Синхронизирует файлы между локальной директорией и облачным хранилищем.

    Args:
        connector (YandexDiskConnector): Объект для работы с облачным хранилищем.
        local_dir (str): Путь к локальной директории.
        log (logger): Логгер для записи информации о процессе синхронизации.
    Raises:
        Exception: В случае ошибки при синхронизации файлов.
    """
    try:
        # Получаем информацию о файлах
        cloud_files = connector.get_info()
        local_files = os.listdir(local_dir)

        # Удаляем файлы из облака, которых нет локально
        for cloud_file in cloud_files:
            if cloud_file not in local_files:
                connector.delete(filename=cloud_file)
                log.info(f"Удалён файл из облака: {cloud_file}")

        # Загружаем новые и измененные файлы
        for local_file in local_files:
            local_file_path = os.path.join(local_dir, local_file)
            if local_file not in cloud_files:
                connector.load(path=local_file_path)
                log.info(f"Загружен новый файл в облако: {local_file}")

            else:
                # Проверяем хеши файлов для определения изменений
                local_file_hash = calculate_file_hash(local_file_path)
                cloud_file_hash = cloud_files[local_file]

                if local_file_hash != cloud_file_hash:
                    connector.reload(path=local_file_path)
                    log.info(f"Перезаписан файл в облаке: {local_file}")

    except Exception as exc:
        log.error(f"Ошибка синхронизации! {str(exc)}")