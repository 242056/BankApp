"""
Утилиты для валидации паролей
"""
import re
from typing import List, Tuple


def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    Проверка надежности пароля
    
    Args:
        password: Пароль для проверки
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    # Минимальная длина
    if len(password) < 8:
        errors.append("Пароль должен содержать минимум 8 символов")
    
    # Максимальная длина (защита от DoS через bcrypt)
    if len(password) > 72:
        errors.append("Пароль не должен превышать 72 символа")
    
    # Наличие заглавной буквы
    if not re.search(r'[A-Z]', password):
        errors.append("Пароль должен содержать хотя бы одну заглавную букву")
    
    # Наличие строчной буквы
    if not re.search(r'[a-z]', password):
        errors.append("Пароль должен содержать хотя бы одну строчную букву")
    
    # Наличие цифры
    if not re.search(r'\d', password):
        errors.append("Пароль должен содержать хотя бы одну цифру")
    
    # Наличие специального символа
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Пароль должен содержать хотя бы один специальный символ (!@#$%^&* и т.д.)")
    
    # Проверка на распространенные пароли
    common_passwords = [
        'password', '12345678', 'qwerty', 'abc123', 'password1',
        '12345', '1234567890', 'letmein', 'welcome', 'monkey'
    ]
    if password.lower() in common_passwords:
        errors.append("Этот пароль слишком распространенный и небезопасный")
    
    return (len(errors) == 0, errors)


def get_password_strength_score(password: str) -> int:
    """
    Оценка надежности пароля от 0 до 100
    
    Args:
        password: Пароль для оценки
        
    Returns:
        int: Оценка от 0 до 100
    """
    score = 0
    
    # Длина (до 30 баллов)
    length_score = min(len(password) * 2, 30)
    score += length_score
    
    # Разнообразие символов (до 40 баллов)
    if re.search(r'[a-z]', password):
        score += 10
    if re.search(r'[A-Z]', password):
        score += 10
    if re.search(r'\d', password):
        score += 10
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 10
    
    # Сложность (до 30 баллов)
    # Проверка на последовательности
    if not re.search(r'(012|123|234|345|456|567|678|789|abc|bcd|cde)', password.lower()):
        score += 10
    
    # Проверка на повторяющиеся символы
    if not re.search(r'(.)\1{2,}', password):
        score += 10
    
    # Длина больше 12 символов
    if len(password) >= 12:
        score += 10
    
    return min(score, 100)
