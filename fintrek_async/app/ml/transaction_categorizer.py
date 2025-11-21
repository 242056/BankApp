"""
Модель машинного обучения для автоматической категоризации транзакций
"""
import re
from typing import Optional, Dict, List
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fintrek_async.app.models.transaction import Transaction
from fintrek_async.app.models.category import Category, CategoryType

logger = logging.getLogger(__name__)


class TransactionCategorizer:
    """Классификатор транзакций на основе правил и ML"""
    
    def __init__(self):
        # Словари ключевых слов для категоризации
        self.expense_keywords = {
            "Продукты": [
                "магнит", "пятерочка", "перекресток", "лента", "ашан", "дикси",
                "супермаркет", "продукты", "grocery", "market", "food"
            ],
            "Транспорт": [
                "яндекс.такси", "uber", "bolt", "метро", "автобус", "бензин",
                "азс", "заправка", "парковка", "parking", "taxi", "transport"
            ],
            "Жилье": [
                "коммунальные", "квартплата", "жкх", "электричество", "газ",
                "вода", "интернет", "домофон", "rent", "utilities"
            ],
            "Здоровье": [
                "аптека", "поликлиника", "больница", "врач", "лекарства",
                "медицина", "pharmacy", "hospital", "doctor", "medicine"
            ],
            "Развлечения": [
                "кино", "театр", "концерт", "музей", "парк", "развлечения",
                "cinema", "entertainment", "game", "игры", "steam", "playstation"
            ],
            "Одежда": [
                "zara", "h&m", "uniqlo", "одежда", "обувь", "магазин одежды",
                "fashion", "clothes", "shoes", "clothing"
            ],
            "Образование": [
                "курсы", "обучение", "университет", "школа", "книги",
                "education", "course", "university", "school", "books"
            ],
            "Кафе и рестораны": [
                "кафе", "ресторан", "макдоналдс", "kfc", "бургер", "пицца",
                "coffee", "restaurant", "cafe", "bar", "pub", "starbucks"
            ],
            "Связь": [
                "мтс", "мегафон", "билайн", "теле2", "связь", "мобильная связь",
                "mobile", "phone", "телефон", "интернет"
            ],
        }
        
        self.income_keywords = {
            "Зарплата": [
                "зарплата", "заработная плата", "salary", "wage", "payment",
                "оплата труда", "выплата"
            ],
            "Фриланс": [
                "фриланс", "freelance", "upwork", "fiverr", "заказ",
                "проект", "honorarium"
            ],
            "Инвестиции": [
                "дивиденды", "проценты", "купон", "dividend", "interest",
                "investment", "брокер", "broker"
            ],
            "Подарки": [
                "подарок", "gift", "перевод от", "transfer from"
            ],
        }
    
    async def categorize(
        self,
        description: str,
        merchant_name: Optional[str],
        amount: float,
        db: AsyncSession
    ) -> Optional[str]:
        """
        Определить категорию транзакции
        
        Args:
            description: Описание транзакции
            merchant_name: Название продавца
            amount: Сумма транзакции
            db: Database session
            
        Returns:
            ID категории или None
        """
        # Объединить описание и название продавца
        text = f"{description or ''} {merchant_name or ''}".lower()
        
        # Определить тип транзакции (доход или расход)
        is_expense = amount < 0
        
        # Выбрать соответствующий словарь ключевых слов
        keywords_dict = self.expense_keywords if is_expense else self.income_keywords
        category_type = CategoryType.EXPENSE if is_expense else CategoryType.INCOME
        
        # Поиск совпадений с ключевыми словами
        best_match = None
        max_matches = 0
        
        for category_name, keywords in keywords_dict.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > max_matches:
                max_matches = matches
                best_match = category_name
        
        # Если найдено совпадение, вернуть ID категории
        if best_match:
            result = await db.execute(select(Category).filter(
                Category.name == best_match,
                Category.category_type == category_type,
                Category.is_system == True
            ))
            category = result.scalars().first()
            
            if category:
                return str(category.id)
        
        # Если не найдено совпадений, вернуть категорию "Другое"
        result = await db.execute(select(Category).filter(
            Category.name == "Другое",
            Category.category_type == category_type,
            Category.is_system == True
        ))
        other_category = result.scalars().first()
        
        return str(other_category.id) if other_category else None
    
    async def categorize_transaction(self, transaction: Transaction, db: AsyncSession) -> bool:
        """
        Категоризировать транзакцию и обновить в БД
        
        Args:
            transaction: Объект транзакции
            db: Database session
            
        Returns:
            True если категория была установлена
        """
        if transaction.category_id:
            return False  # Уже категоризирована
        
        category_id = await self.categorize(
            description=transaction.description,
            merchant_name=transaction.merchant_name,
            amount=float(transaction.amount),
            db=db
        )
        
        if category_id:
            transaction.category_id = category_id
            await db.commit()
            logger.info(f"Transaction {transaction.id} categorized as {category_id}")
            return True
        
        return False
    
    async def batch_categorize(self, db: AsyncSession, limit: int = 100) -> int:
        """
        Категоризировать пакет некатегоризированных транзакций
        
        Args:
            db: Database session
            limit: Максимальное количество транзакций
            
        Returns:
            Количество категоризированных транзакций
        """
        # Получить некатегоризированные транзакции
        result = await db.execute(select(Transaction).filter(
            Transaction.category_id == None
        ).limit(limit))
        transactions = result.scalars().all()
        
        categorized_count = 0
        
        for transaction in transactions:
            if await self.categorize_transaction(transaction, db):
                categorized_count += 1
        
        logger.info(f"Batch categorized {categorized_count} transactions")
        return categorized_count


# Singleton instance
transaction_categorizer = TransactionCategorizer()
