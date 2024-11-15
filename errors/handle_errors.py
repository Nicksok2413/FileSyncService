import requests


def handle_errors(exc) -> None:
    """Обрабатывает ошибки запросов.

    Args:
        exc (Exception): Исключение, которое нужно обработать.

    Raises:
         ConnectionError: Если возникли проблемы с соединением.
         FileNotFoundError: Если файл не найден на облаке.
         PermissionError: Если доступ запрещен или ошибка авторизации.
         requests.HTTPError: Для других HTTP ошибок.
         Exception: Для любых других исключений.
    """
    if isinstance(exc, requests.exceptions.ConnectTimeout):
        raise ConnectionError("Не удалось установить соединение с облачным сервисом.")
    elif isinstance(exc, requests.exceptions.ReadTimeout):
        raise ConnectionError("Запрос не завершился вовремя.")
    elif isinstance(exc, requests.exceptions.HTTPError):
        if exc.response.status_code == 404:
            raise FileNotFoundError(f"404 - файл не найден на облаке.")
        elif exc.response.status_code == 403:
            raise PermissionError(f"Доступ запрещен: 403 - проверьте права доступа.")
        elif exc.response.status_code == 401:
            raise PermissionError(f"Ошибка авторизации: 401 - проверьте токен доступа.")
        elif exc.response.status_code == 500:
            raise Exception(f"500 - внутренняя ошибка сервера облачного сервиса.")
        else:
            raise requests.HTTPError(f"Ошибка HTTP: {exc.response.status_code} - {exc}")
    else:
        raise Exception(f"Произошла ошибка: {str(exc)}")