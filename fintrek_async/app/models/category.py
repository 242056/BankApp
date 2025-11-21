"""
Модель категории для SQLAlchemy
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

try:
    from fintrek_async.app.db.base import Base
except ImportError:
    from ..db.base import Base


class CategoryType(str, enum.Enum):
    """Типы категорий"""
    INCOME = "income"
    EXPENSE = "expense"


class Category(Base):
    """Модель категории транзакций"""
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Информация о категории
    name = Column(String, nullable=False)
    category_type = Column(Enum(CategoryType), nullable=False)
    icon = Column(String, nullable=True)  # Название иконки или emoji
    color = Column(String(7), nullable=True)  # Цвет в формате #RRGGBB
    
    # Системная категория (не может быть удалена пользователем)
    is_system = Column(Boolean, default=False, nullable=False)
    
    # Родительская категория (для подкатегорий)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=True)
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Отношения
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, type={self.category_type})>"
