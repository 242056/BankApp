"""
Кастомные исключения для приложения
"""


class FinTrekException(Exception):
    """Базовое исключение для всех кастомных ошибок приложения"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseConnectionError(FinTrekException):
    """Ошибка подключения к базе данных"""
    pass


class RedisConnectionError(FinTrekException):
    """Ошибка подключения к Redis"""
    pass


class ExternalAPIError(FinTrekException):
    """Ошибка при обращении к внешнему API"""
    def __init__(self, message: str, status_code: int = None, details: dict = None):
        super().__init__(message, details)
        self.status_code = status_code


class VBankAPIError(ExternalAPIError):
    """Ошибка при обращении к VBank API"""
    pass


class OpenBankingAPIError(ExternalAPIError):
    """Ошибка при обращении к Open Banking API"""
    pass


class AuthenticationError(FinTrekException):
    """Ошибка аутентификации"""
    pass


class AuthorizationError(FinTrekException):
    """Ошибка авторизации (недостаточно прав)"""
    pass


class ResourceNotFoundError(FinTrekException):
    """Ресурс не найден"""
    pass


class ValidationError(FinTrekException):
    """Ошибка валидации данных"""
    pass
