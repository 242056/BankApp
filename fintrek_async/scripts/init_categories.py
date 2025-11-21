"""
Скрипт для создания начальных системных категорий (ASYNC версия)
"""
import sys
import os
import asyncio

# Добавить путь к приложению
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fintrek_async.app.db.session import AsyncSessionLocal
from fintrek_async.app.models.category import Category, CategoryType
from sqlalchemy import select, func
import uuid


async def create_default_categories():
    """Создать системные категории по умолчанию"""
    async with AsyncSessionLocal() as db:
        try:
            # Проверить существуют ли уже системные категории
            result = await db.execute(
                select(func.count(Category.id)).where(Category.is_system == True)
            )
            existing = result.scalar()
            if existing > 0:
                print(f"Системные категории уже существуют ({existing} шт.)")
                return
        
        # Категории расходов
        expense_categories = [
            {"name": "Продукты", "icon": "🛒", "color": "#FF6B6B"},
            {"name": "Транспорт", "icon": "🚗", "color": "#4ECDC4"},
            {"name": "Жилье", "icon": "🏠", "color": "#45B7D1"},
            {"name": "Здоровье", "icon": "⚕️", "color": "#96CEB4"},
            {"name": "Развлечения", "icon": "🎮", "color": "#FFEAA7"},
            {"name": "Одежда", "icon": "👔", "color": "#DFE6E9"},
            {"name": "Образование", "icon": "📚", "color": "#74B9FF"},
            {"name": "Кафе и рестораны", "icon": "🍽️", "color": "#FD79A8"},
            {"name": "Связь", "icon": "📱", "color": "#A29BFE"},
            {"name": "Другое", "icon": "📦", "color": "#B2BEC3"},
        ]
        
        # Категории доходов
        income_categories = [
            {"name": "Зарплата", "icon": "💰", "color": "#00B894"},
            {"name": "Фриланс", "icon": "💻", "color": "#00CEC9"},
            {"name": "Инвестиции", "icon": "📈", "color": "#FDCB6E"},
            {"name": "Подарки", "icon": "🎁", "color": "#E17055"},
            {"name": "Другое", "icon": "💵", "color": "#636E72"},
        ]
        
            created_count = 0
            
            # Создать категории расходов
            for cat_data in expense_categories:
                category = Category(
                    id=uuid.uuid4(),
                    user_id=None,  # Системная категория
                    name=cat_data["name"],
                    category_type=CategoryType.EXPENSE,
                    icon=cat_data["icon"],
                    color=cat_data["color"],
                    is_system=True
                )
                db.add(category)
                created_count += 1
            
            # Создать категории доходов
            for cat_data in income_categories:
                category = Category(
                    id=uuid.uuid4(),
                    user_id=None,  # Системная категория
                    name=cat_data["name"],
                    category_type=CategoryType.INCOME,
                    icon=cat_data["icon"],
                    color=cat_data["color"],
                    is_system=True
                )
                db.add(category)
                created_count += 1
            
            await db.commit()
            print(f"✅ Создано {created_count} системных категорий")
            
        except Exception as e:
            print(f"❌ Ошибка при создании категорий: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(create_default_categories())
