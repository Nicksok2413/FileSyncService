import os
import requests


class YandexDiskConnector:
    def __init__(self, token: str, cloud_dir: str) -> None:
        self.__token = token
        self.__cloud_dir = cloud_dir
        self.__headers = {"Content-Type": "application/json", "Accept": "application/json",
                        "Authorization": f"OAuth {self.__token}"}
        self.__url = "https://cloud-api.yandex.net/v1/disk/resources"


    def get_cloud_files(self) -> dict[str, str]:
        """
        Получает информацию о файлах в облачном хранилище.

        Returns:
            dict[str, str]: Словарь с именами файлов и временем их последнего изменения.
        Raises:
            requests.HTTPError: В случае ошибки при выполнении запроса.
        """
        response = requests.get(f"{self.__url}?path={self.__cloud_dir}",
                                headers=self.__headers)
        response.raise_for_status()

        files_info = response.json().get("_embedded", {}).get("items", [])

        return {file["name"]: file["modified"] for file in files_info}


    def upload_file(self, file_path: str, overwrite=False) -> None:
        """
        Загружает файл на Яндекс Диск.

        Args:
            file_path (str): Путь к локальному файлу для загрузки.
            overwrite (bool): Флаг перезаписи файла, по умолчанию False.
        Raises:
            KeyError: В случае ошибки при выполнении запроса.
        """
        with open(file_path, 'rb') as file_to_load:
            response = requests.get(f"{self.__url}/upload?path={self.__cloud_dir}/{os.path.basename(file_path)}&overwrite={overwrite}", headers=self.__headers).json()
            try:
                requests.put(response["href"], files={"file": file_to_load})
            except KeyError:
                print(response)


    def reupload_file(self, file_path: str) -> None:
        """
        Повторно загружает измененный файл на Яндекс Диск.

        Args:
            file_path (str): Путь к локальному файлу для повторной загрузки.
        Raises:
            KeyError: В случае ошибки при выполнении запроса.
        """
        self.upload_file(file_path, overwrite=True)  # Переиспользует метод загрузки файла с флагом перезаписи = True


    def delete_file(self, file_name: str) -> None:
        """
        Удаляет файл из Яндекс Диска по имени.

        Args:
            file_name (str): Имя файла для удаления.
        Raises:
            requests.HTTPError: В случае ошибки при выполнении запроса.
        """
        response = requests.delete(f"{self.__url}?path={self.__cloud_dir}/{file_name}", headers=self.__headers)
        response.raise_for_status()