"""
Прогностическая модель для предсказания будущих доходов и расходов
"""
from typing import Dict, List
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, select
import logging

from fintrek_async.app.models.transaction import Transaction, TransactionType

logger = logging.getLogger(__name__)


class ForecastingModel:
    """Модель прогнозирования финансовых показателей"""
    
    async def forecast_next_month_spending(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Dict:
        """
        Прогнозировать расходы на следующий месяц
        
        Args:
            db: Database session
            user_id: ID пользователя
            
        Returns:
            Прогноз расходов
        """
        # Получить данные за последние 6 месяцев
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=180)
        
        result = await db.execute(
            select(
                func.date_trunc('month', Transaction.transaction_date).label('month'),
                func.sum(Transaction.amount).label('total')
            ).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == TransactionType.EXPENSE,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            ).group_by('month').order_by('month')
        )
        monthly_spending = result.all()
        
        if not monthly_spending:
            return {
                'forecast': 0,
                'confidence': 'low',
                'message': 'Недостаточно данных для прогноза'
            }
        
        # Простое скользящее среднее
        spending_values = [float(total) for _, total in monthly_spending]
        avg_spending = sum(spending_values) / len(spending_values)
        
        # Вычислить тренд (линейная регрессия)
        if len(spending_values) >= 3:
            # Простая линейная регрессия
            n = len(spending_values)
            x = list(range(n))
            y = spending_values
            
            x_mean = sum(x) / n
            y_mean = sum(y) / n
            
            numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            if denominator != 0:
                slope = numerator / denominator
                intercept = y_mean - slope * x_mean
                
                # Прогноз на следующий месяц
                next_month_forecast = slope * n + intercept
            else:
                next_month_forecast = avg_spending
        else:
            next_month_forecast = avg_spending
        
        # Определить уровень уверенности
        if len(spending_values) >= 6:
            confidence = 'high'
        elif len(spending_values) >= 3:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        # Вычислить диапазон прогноза (±15%)
        lower_bound = next_month_forecast * 0.85
        upper_bound = next_month_forecast * 1.15
        
        return {
            'forecast': round(next_month_forecast, 2),
            'lower_bound': round(lower_bound, 2),
            'upper_bound': round(upper_bound, 2),
            'confidence': confidence,
            'historical_average': round(avg_spending, 2),
            'trend': 'increasing' if next_month_forecast > avg_spending else 'decreasing',
            'data_points': len(spending_values)
        }
    
    async def forecast_next_month_income(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Dict:
        """
        Прогнозировать доход на следующий месяц
        
        Args:
            db: Database session
            user_id: ID пользователя
            
        Returns:
            Прогноз дохода
        """
        # Получить данные за последние 6 месяцев
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=180)
        
        result = await db.execute(
            select(
                func.date_trunc('month', Transaction.transaction_date).label('month'),
                func.sum(Transaction.amount).label('total')
            ).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == TransactionType.INCOME,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            ).group_by('month').order_by('month')
        )
        monthly_income = result.all()
        
        if not monthly_income:
            return {
                'forecast': 0,
                'confidence': 'low',
                'message': 'Недостаточно данных для прогноза'
            }
        
        # Среднее значение
        income_values = [float(total) for _, total in monthly_income]
        avg_income = sum(income_values) / len(income_values)
        
        # Для дохода обычно используем медиану, так как она менее чувствительна к выбросам
        sorted_income = sorted(income_values)
        n = len(sorted_income)
        
        if n % 2 == 0:
            median_income = (sorted_income[n//2 - 1] + sorted_income[n//2]) / 2
        else:
            median_income = sorted_income[n//2]
        
        # Определить уровень уверенности
        if len(income_values) >= 6:
            confidence = 'high'
        elif len(income_values) >= 3:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        return {
            'forecast': round(median_income, 2),
            'average': round(avg_income, 2),
            'confidence': confidence,
            'data_points': len(income_values)
        }
    
    async def forecast_balance(
        self,
        db: AsyncSession,
        user_id: str,
        months_ahead: int = 3
    ) -> List[Dict]:
        """
        Прогнозировать баланс на несколько месяцев вперед
        
        Args:
            db: Database session
            user_id: ID пользователя
            months_ahead: Количество месяцев для прогноза
            
        Returns:
            Список прогнозов по месяцам
        """
        # Получить текущий баланс
        from fintrek_async.app.models.account import Account
        
        result = await db.execute(select(Account).filter(Account.user_id == user_id))
        accounts = result.scalars().all()
        current_balance = sum(float(acc.balance) for acc in accounts)
        
        # Получить прогнозы дохода и расходов
        income_forecast = await self.forecast_next_month_income(db, user_id)
        spending_forecast = await self.forecast_next_month_spending(db, user_id)
        
        monthly_income = income_forecast.get('forecast', 0)
        monthly_spending = spending_forecast.get('forecast', 0)
        monthly_net = monthly_income - monthly_spending
        
        # Построить прогноз на несколько месяцев
        forecasts = []
        balance = current_balance
        
        for month in range(1, months_ahead + 1):
            balance += monthly_net
            
            next_month = datetime.utcnow() + timedelta(days=30 * month)
            
            forecasts.append({
                'month': next_month.strftime('%Y-%m'),
                'projected_balance': round(balance, 2),
                'projected_income': round(monthly_income, 2),
                'projected_spending': round(monthly_spending, 2),
                'net_change': round(monthly_net, 2)
            })
        
        return forecasts
    
    async def calculate_financial_health_score(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Dict:
        """
        Вычислить показатель финансового здоровья (0-100)
        
        Args:
            db: Database session
            user_id: ID пользователя
            
        Returns:
            Оценка и детали
        """
        score = 0
        max_score = 100
        details = []
        
        # 1. Уровень сбережений (30 баллов)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        result = await db.execute(
            select(func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == TransactionType.INCOME,
                    Transaction.transaction_date >= start_date
                )
            )
        )
        total_income = result.scalar() or Decimal(0)
        
        result = await db.execute(
            select(func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == TransactionType.EXPENSE,
                    Transaction.transaction_date >= start_date
                )
            )
        )
        total_expenses = result.scalar() or Decimal(0)
        
        if total_income > 0:
            savings_rate = ((total_income - total_expenses) / total_income) * 100
            
            if savings_rate >= 20:
                savings_score = 30
            elif savings_rate >= 10:
                savings_score = 20
            elif savings_rate >= 0:
                savings_score = 10
            else:
                savings_score = 0
            
            score += savings_score
            details.append({
                'category': 'Уровень сбережений',
                'score': savings_score,
                'max_score': 30,
                'value': f'{savings_rate:.1f}%'
            })
        
        # 2. Стабильность дохода (20 баллов)
        income_forecast = await self.forecast_next_month_income(db, user_id)
        
        if income_forecast['confidence'] == 'high':
            income_score = 20
        elif income_forecast['confidence'] == 'medium':
            income_score = 12
        else:
            income_score = 5
        
        score += income_score
        details.append({
            'category': 'Стабильность дохода',
            'score': income_score,
            'max_score': 20,
            'value': income_forecast['confidence']
        })
        
        # 3. Контроль расходов (25 баллов)
        spending_forecast = await self.forecast_next_month_spending(db, user_id)
        
        if spending_forecast.get('trend') == 'decreasing':
            spending_score = 25
        elif spending_forecast.get('trend') == 'stable':
            spending_score = 15
        else:
            spending_score = 5
        
        score += spending_score
        details.append({
            'category': 'Контроль расходов',
            'score': spending_score,
            'max_score': 25,
            'value': spending_forecast.get('trend', 'unknown')
        })
        
        # 4. Баланс счетов (15 баллов)
        from fintrek_async.app.models.account import Account
        
        result = await db.execute(select(Account).filter(Account.user_id == user_id))
        accounts = result.scalars().all()
        total_balance = sum(float(acc.balance) for acc in accounts)
        
        # Оценить баланс относительно месячных расходов
        if total_expenses > 0:
            months_of_expenses = total_balance / float(total_expenses)
            
            if months_of_expenses >= 6:
                balance_score = 15
            elif months_of_expenses >= 3:
                balance_score = 10
            elif months_of_expenses >= 1:
                balance_score = 5
            else:
                balance_score = 0
        else:
            balance_score = 10
        
        score += balance_score
        details.append({
            'category': 'Резервный фонд',
            'score': balance_score,
            'max_score': 15,
            'value': f'{total_balance:.2f} руб'
        })
        
        # 5. Диверсификация (10 баллов)
        num_accounts = len(accounts)
        
        if num_accounts >= 3:
            diversification_score = 10
        elif num_accounts == 2:
            diversification_score = 7
        elif num_accounts == 1:
            diversification_score = 3
        else:
            diversification_score = 0
        
        score += diversification_score
        details.append({
            'category': 'Диверсификация',
            'score': diversification_score,
            'max_score': 10,
            'value': f'{num_accounts} счетов'
        })
        
        # Определить уровень
        if score >= 80:
            level = 'Отличное'
            color = 'green'
        elif score >= 60:
            level = 'Хорошее'
            color = 'lightgreen'
        elif score >= 40:
            level = 'Удовлетворительное'
            color = 'yellow'
        else:
            level = 'Требует внимания'
            color = 'red'
        
        return {
            'score': score,
            'max_score': max_score,
            'percentage': round((score / max_score) * 100, 1),
            'level': level,
            'color': color,
            'details': details
        }


# Singleton instance
forecasting_model = ForecastingModel()
