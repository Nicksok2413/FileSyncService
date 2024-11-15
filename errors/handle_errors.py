import requests


def handle_errors(exc) -> None:
    """Обрабатывает ошибки запросов."""
    if isinstance(exc, requests.exceptions.ConnectTimeout):
        raise ConnectionError("Не удалось установить соединение с облачным сервисом.")
    elif isinstance(exc, requests.exceptions.ReadTimeout):
        raise ConnectionError("Запрос не завершился вовремя.")
    elif isinstance(exc, requests.exceptions.HTTPError):
        if exc.response.status_code == 404:
            raise FileNotFoundError("Файл не найден на облаке.")
        elif exc.response.status_code == 403:
            raise PermissionError("Доступ запрещен: проверьте права доступа.")
        elif exc.response.status_code == 401:
            raise PermissionError("Ошибка авторизации: проверьте токен доступа.")
        elif exc.response.status_code == 500:
            raise Exception("Внутренняя ошибка сервера облачного сервиса.")
        else:
            raise requests.HTTPError(f"Ошибка HTTP: {exc}")
    else:
        raise Exception(f"Произошла ошибка: {str(exc)}")