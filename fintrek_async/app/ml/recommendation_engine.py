"""
Система рекомендаций для улучшения финансового положения
"""
from typing import List, Dict
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, select

from fintrek_async.app.models.transaction import Transaction, TransactionType
from fintrek_async.app.models.account import Account
from fintrek_async.app.ml.spending_analyzer import spending_analyzer
import logging

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Генератор персонализированных финансовых рекомендаций"""
    
    async def generate_recommendations(
        self,
        db: AsyncSession,
        user_id: str
    ) -> List[Dict]:
        """
        Сгенерировать рекомендации для пользователя
        
        Args:
            db: Database session
            user_id: ID пользователя
            
        Returns:
            Список рекомендаций
        """
        recommendations = []
        
        # 1. Анализ повторяющихся платежей
        recurring = await spending_analyzer.detect_recurring_payments(db, user_id)
        if recurring:
            total_subscriptions = sum(r['amount'] for r in recurring)
            recommendations.append({
                'type': 'subscriptions',
                'priority': 'high',
                'title': 'Проверьте ваши подписки',
                'description': f'У вас {len(recurring)} активных подписок на сумму {total_subscriptions:.2f} руб/мес. '
                               f'Возможно, некоторые из них больше не нужны.',
                'action': 'review_subscriptions',
                'potential_savings': total_subscriptions * 0.3  # Предполагаем 30% экономии
            })
        
        # 2. Анализ аномальных расходов
        anomalies = await spending_analyzer.detect_anomalies(db, user_id)
        if len(anomalies) > 3:
            recommendations.append({
                'type': 'anomalies',
                'priority': 'medium',
                'title': 'Обнаружены необычные расходы',
                'description': f'За последний месяц обнаружено {len(anomalies)} необычно больших транзакций. '
                               f'Проверьте их корректность.',
                'action': 'review_anomalies',
                'details': anomalies[:5]  # Топ-5 аномалий
            })
        
        # 3. Анализ трендов
        trends = await spending_analyzer.get_spending_trends(db, user_id)
        if trends['trend'] == 'up' and trends['change_percent'] > 20:
            recommendations.append({
                'type': 'spending_increase',
                'priority': 'high',
                'title': 'Расходы выросли на ' + str(round(trends['change_percent'])) + '%',
                'description': f'В этом месяце вы потратили на {trends["change_percent"]:.0f}% больше, '
                               f'чем в прошлом ({trends["current_month"]:.2f} руб vs {trends["previous_month"]:.2f} руб). '
                               f'Рекомендуем пересмотреть бюджет.',
                'action': 'review_budget'
            })
        
        # 4. Анализ расходов по категориям
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        spending_by_category = await spending_analyzer.get_spending_by_category(
            db, user_id, start_date, end_date
        )
        
        if spending_by_category:
            total_spending = sum(spending_by_category.values())
            
            # Найти категорию с наибольшими расходами
            top_category = max(spending_by_category.items(), key=lambda x: x[1])
            category_percent = (top_category[1] / total_spending) * 100
            
            if category_percent > 40:
                recommendations.append({
                    'type': 'category_optimization',
                    'priority': 'medium',
                    'title': f'Высокие расходы на "{top_category[0]}"',
                    'description': f'Вы тратите {category_percent:.0f}% бюджета ({top_category[1]:.2f} руб) '
                                   f'на категорию "{top_category[0]}". Возможно, стоит оптимизировать эти расходы.',
                    'action': 'optimize_category',
                    'category': top_category[0],
                    'potential_savings': top_category[1] * 0.2  # 20% экономии
                })
        
        # 5. Рекомендации по сбережениям
        total_income = await self._get_total_income(db, user_id, start_date, end_date)
        total_expenses = sum(spending_by_category.values())
        
        if total_income > 0:
            savings_rate = ((total_income - total_expenses) / total_income) * 100
            
            if savings_rate < 10:
                recommendations.append({
                    'type': 'savings',
                    'priority': 'high',
                    'title': 'Низкий уровень сбережений',
                    'description': f'Вы откладываете только {savings_rate:.1f}% дохода. '
                                   f'Финансовые эксперты рекомендуют откладывать минимум 10-20% дохода.',
                    'action': 'increase_savings',
                    'recommended_amount': total_income * 0.15  # 15% дохода
                })
            elif savings_rate > 30:
                recommendations.append({
                    'type': 'investment',
                    'priority': 'low',
                    'title': 'Отличный уровень сбережений!',
                    'description': f'Вы откладываете {savings_rate:.1f}% дохода. '
                                   f'Рассмотрите возможность инвестирования части средств для увеличения доходности.',
                    'action': 'consider_investment'
                })
        
        # 6. Проверка баланса счетов
        result = await db.execute(select(Account).filter(Account.user_id == user_id))
        accounts = result.scalars().all()
        low_balance_accounts = [acc for acc in accounts if acc.balance < 1000]
        
        if low_balance_accounts:
            recommendations.append({
                'type': 'low_balance',
                'priority': 'medium',
                'title': 'Низкий баланс на счетах',
                'description': f'На {len(low_balance_accounts)} счетах баланс ниже 1000 руб. '
                               f'Рекомендуем пополнить счета для избежания овердрафта.',
                'action': 'top_up_accounts',
                'accounts': [
                    {'name': acc.account_name, 'balance': float(acc.balance)}
                    for acc in low_balance_accounts
                ]
            })
        
        # Сортировать по приоритету
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return recommendations
    
    async def _get_total_income(
        self,
        db: AsyncSession,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Получить общий доход за период"""
        result = await db.execute(
            select(func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == TransactionType.INCOME,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            )
        )
        total = result.scalar()
        
        return float(total) if total else 0.0
    
    async def generate_proactive_advice(
        self,
        db: AsyncSession,
        user_id: str,
        scenario: str
    ) -> Dict:
        """
        Сгенерировать проактивный совет для конкретного сценария
        
        Args:
            db: Database session
            user_id: ID пользователя
            scenario: Тип сценария (coffee, subscription, etc.)
            
        Returns:
            Совет с расчетами
        """
        if scenario == 'coffee':
            # Пример: "Вы тратите на кофе X руб/месяц"
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            result = await db.execute(
                select(func.sum(Transaction.amount)).filter(
                    and_(
                        Transaction.user_id == user_id,
                        Transaction.transaction_type == TransactionType.EXPENSE,
                        Transaction.transaction_date >= start_date,
                        Transaction.transaction_date <= end_date,
                        func.lower(Transaction.description).contains('кофе')
                    )
                )
            )
            coffee_spending = result.scalar() or Decimal(0)
            
            if coffee_spending > 1000:
                yearly_savings = float(coffee_spending) * 12 * 0.5
                return {
                    'scenario': 'coffee',
                    'current_spending': float(coffee_spending),
                    'message': f'Вы тратите {float(coffee_spending):.2f} руб/месяц на кофе. '
                               f'Если сократить эти расходы на 50%, можно сэкономить '
                               f'{yearly_savings:.2f} руб в год.',
                    'potential_savings': yearly_savings
                }
        
        return {
            'scenario': scenario,
            'message': 'Недостаточно данных для анализа'
        }


# Singleton instance
recommendation_engine = RecommendationEngine()
