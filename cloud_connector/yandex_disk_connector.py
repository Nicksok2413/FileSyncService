import os
import requests

from errors.handle_errors import handle_errors


class YandexDiskConnector:
    def __init__(self, token: str, cloud_dir: str) -> None:
        """
        Инициализирует объект YandexDiskConnector.

        Args:
            token (str): Токен доступа к Яндекс Диску.
            cloud_dir (str): Путь к облачной директории на Яндекс Диске.
        """
        self.__token = token
        self.__cloud_dir = cloud_dir
        self.__url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.__timeout = (5, 10)  # (connect timeout, read timeout)
        self.__headers = {"Content-Type": "application/json", "Accept": "application/json",
                        "Authorization": f"OAuth {self.__token}"}


    def __check_directory_exists(self) -> None:
        """Проверяет существование облачной директории.

        Raises:
            FileNotFoundError: Если облачная директория не найдена.
            ConnectionError: Если возникли проблемы с соединением.
            PermissionError: Если доступ запрещен или ошибка авторизации.
            requests.HTTPError: Для других HTTP ошибок.
        """
        try:
            response = requests.get(f"{self.__url}?path={self.__cloud_dir}", headers=self.__headers,
                                    timeout=self.__timeout)
            response.raise_for_status()  # Проверка на ошибки HTTP

        except requests.HTTPError as http_err:
            if http_err.response.status_code == 404:
                raise FileNotFoundError(f"404 - облачная директория '{self.__cloud_dir}' не найдена.")
            else:
                handle_errors(http_err)


    def get_info(self) -> dict[str, str]:
        """
        Получает информацию о файлах в облачном хранилище.

        Returns:
            dict[str, str]: Словарь с именами файлов и значениями их хеша.
        Raises:
            ConnectionError: Если возникли проблемы с соединением.
            PermissionError: Если доступ запрещен или ошибка авторизации.
            requests.HTTPError: Для других HTTP ошибок.
            Exception: Для любых других исключений.
        """
        self.__check_directory_exists()  # Проверка существования директории

        try:
            response = requests.get(f"{self.__url}?path={self.__cloud_dir}",
                                    headers=self.__headers, timeout=self.__timeout)
            response.raise_for_status()  #  Проверка на ошибки HTTP

            files_info = response.json().get("_embedded", {}).get("items", [])

            # Если папка пуста, возвращаем пустой словарь
            if not files_info:
                return {}

            return {file["name"]: file["md5"] for file in files_info}

        except Exception as exc:
            handle_errors(exc)


    def load(self, path: str, overwrite: bool = False) -> None:
        """
        Загружает файл на Яндекс Диск.

        Args:
            path (str): Путь к локальному файлу для загрузки.
            overwrite (bool): Флаг перезаписи файла, по умолчанию False.
        Raises:
            ValueError: Если не удается получить ссылку для загрузки.
            FileNotFoundError: Если указанный файл не найден.
            ConnectionError: Если возникли проблемы с соединением.
            PermissionError: Если доступ запрещен или ошибка авторизации.
            requests.HTTPError: Для других HTTP ошибок.
            Exception: Для любых других исключений.
        """
        self.__check_directory_exists()  # Проверка существования директории

        if not os.path.isfile(path):
            raise FileNotFoundError(f"Файл не найден: {path}")

        try:
            with open(path, 'rb') as file_to_load:
                response = requests.get(
                    f"{self.__url}/upload?path={self.__cloud_dir}/{os.path.basename(path)}&overwrite={overwrite}",
                    headers=self.__headers, timeout=self.__timeout
                )
                response.raise_for_status()  #  Проверка на ошибки HTTP

                upload_url = response.json().get("href")

                if not upload_url:
                    raise ValueError("Не удалось получить ссылку для загрузки.")

                put_response = requests.put(upload_url, files={"file": file_to_load}, timeout=self.__timeout)
                put_response.raise_for_status() #  Проверка на ошибки при загрузке

        except Exception as exc:
            handle_errors(exc)


    def reload(self, path: str) -> None:
        """
        Повторно загружает измененный файл на Яндекс Диск.

        Args:
            path (str): Путь к локальному файлу для повторной загрузки.
        Raises:
            ValueError: Если не удается получить ссылку для загрузки.
            FileNotFoundError: Если указанный файл не найден.
            ConnectionError: Если возникли проблемы с соединением.
            PermissionError: Если доступ запрещен или ошибка авторизации.
            requests.HTTPError: Для других HTTP ошибок.
            Exception: Для любых других исключений.
        """
        self.load(path, overwrite=True)  # Использует метод загрузки файла с флагом перезаписи overwrite = True


    def delete(self, filename: str) -> None:
        """
        Удаляет файл из Яндекс Диска по имени.

        Args:
            filename (str): Имя файла для удаления.
        Raises:
            ValueError: Если имя файла не указано.
            FileNotFoundError: Если указанный файл не найден.
            ConnectionError: Если возникли проблемы с соединением.
            PermissionError: Если доступ запрещен или ошибка авторизации.
            requests.HTTPError: Для других HTTP ошибок.
            Exception: Для любых других исключений.
        """
        self.__check_directory_exists()  # Проверка существования директории

        if not filename:
            raise ValueError("Имя файла не может быть пустым.")

        try:
            response = requests.delete(f"{self.__url}?path={self.__cloud_dir}/{filename}",
                                       headers=self.__headers, timeout=self.__timeout)
            response.raise_for_status()  #  Проверка на ошибки HTTP

        except Exception as exc:
            handle_errors(exc)