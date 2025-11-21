"""
Pydantic схемы для Category
"""
from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from typing import Optional
from fintrek_async.app.models.category import CategoryType


class CategoryBase(BaseModel):
    """Базовая схема категории"""
    name: str = Field(..., min_length=1, max_length=100, description="Название категории")
    category_type: CategoryType = Field(..., description="Тип категории")
    icon: Optional[str] = Field(None, max_length=50, description="Иконка или emoji")
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Цвет в формате #RRGGBB")


class CategoryCreate(CategoryBase):
    """Схема для создания категории"""
    parent_id: Optional[UUID4] = Field(
        default=None,
        description="ID родительской категории (опционально, должен быть валидным UUID если указан, или null для корневой категории)",
        json_schema_extra={"example": None}
    )


class CategoryUpdate(BaseModel):
    """Схема для обновления категории"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class CategoryResponse(CategoryBase):
    """Схема ответа с категорией"""
    id: UUID4
    user_id: Optional[UUID4]
    parent_id: Optional[UUID4]
    is_system: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Схема для списка категорий"""
    categories: list[CategoryResponse]
    total: int
