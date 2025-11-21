"""
Эндпоинты для управления категориями
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List
from uuid import UUID

from fintrek_async.app.api.v1.deps import get_db, get_current_user
from fintrek_async.app.models.user import User
from fintrek_async.app.models.category import Category
from fintrek_async.app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse
)

router = APIRouter()


@router.get("/", response_model=CategoryListResponse)
async def get_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список всех категорий (системных и пользовательских)
    """
    stmt = select(Category).filter(
        or_(
            Category.user_id == current_user.id,
            Category.is_system == True
        )
    )
    result = await db.execute(stmt)
    categories = result.scalars().all()
    
    return CategoryListResponse(
        categories=categories,
        total=len(categories)
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о конкретной категории
    """
    stmt = select(Category).filter(
        Category.id == category_id,
        or_(
            Category.user_id == current_user.id,
            Category.is_system == True
        )
    )
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новую пользовательскую категорию
    
    Требования:
    - name: обязательное поле, название категории
    - category_type: обязательное поле (INCOME или EXPENSE)
    - parent_id: опциональное поле, должен быть валидным UUID существующей категории или null для корневой категории
    - icon: опциональное поле, иконка или emoji
    - color: опциональное поле, цвет в формате #RRGGBB
    """
    # Проверить что родительская категория существует и доступна пользователю
    if category_data.parent_id:
        stmt = select(Category).filter(
            Category.id == category_data.parent_id,
            or_(
                Category.user_id == current_user.id,
                Category.is_system == True
            )
        )
        result = await db.execute(stmt)
        parent = result.scalar_one_or_none()
        
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent category with id {category_data.parent_id} not found or not accessible"
            )
    
    category = Category(
        user_id=current_user.id,
        name=category_data.name,
        category_type=category_data.category_type,
        icon=category_data.icon,
        color=category_data.color,
        parent_id=category_data.parent_id,
        is_system=False
    )
    
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    return category


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить пользовательскую категорию
    """
    category = (await db.execute(select(Category).where(
        Category.id == category_id,
        Category.user_id == current_user.id
    ))).scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    if category.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify system category"
        )
    
    # Обновить только переданные поля
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    await db.commit()
    await db.refresh(category)
    
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить пользовательскую категорию
    """
    category = (await db.execute(select(Category).where(
        Category.id == category_id,
        Category.user_id == current_user.id
    ))).scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    if category.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete system category"
        )
    
    await db.delete(category)
    await db.commit()
    
    return None
