"""
Базовый класс для всех моделей SQLAlchemy
"""
from sqlalchemy.ext.declarative import declarative_base

# Создаем базовый класс для всех моделей
Base = declarative_base()
