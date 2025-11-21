import { apiFetch } from "./client";

// Types reflecting backend responses (kept minimal, extend as needed)
export interface AccountSummaryItem { id: string; name: string; type: string; balance: number; currency: string; percentage: number; }
export interface AccountSummary { total_balance: number; accounts_count: number; accounts: AccountSummaryItem[]; }

export interface IncomeVsExpensesPoint { month: string; income: number; expenses: number; net: number; }
export interface IncomeVsExpenses { months: number; data: IncomeVsExpensesPoint[]; }

export interface SpendingByCategoryItem { category: string; type: string; total: number; count: number; average: number; percentage: number; }
export interface SpendingByCategory { total_spending: number; categories: SpendingByCategoryItem[]; period: { start_date: string; end_date: string; days: number; }; }

export interface AIDashboard {
  financial_health?: { score?: number; change?: number } | number;
  top_recommendations?: Array<any>;
  spending_trends?: any;
  next_month_forecast?: { spending?: any; income?: any };
}

export interface TransactionStatistics {
  period_days: number;
  total_transactions: number;
  income: { count: number; total: number; average: number; largest: number };
  expenses: { count: number; total: number; average: number; largest: number };
  net_income: number;
}

export async function fetchAccountSummary() {
  return apiFetch<AccountSummary>("analytics/account-summary");
}

export async function fetchIncomeVsExpenses(months = 6) {
  return apiFetch<IncomeVsExpenses>("analytics/income-vs-expenses", { query: { months } });
}

export async function fetchSpendingByCategory(params?: { start_date?: string; end_date?: string }) {
  return apiFetch<SpendingByCategory>("analytics/spending-by-category", { query: params });
}

export async function fetchTransactionStatistics(days = 30) {
  return apiFetch<TransactionStatistics>("analytics/transaction-statistics", { query: { days } });
}

export interface DailySpendingTrend {
  period_days: number;
  average_daily_spending: number;
  total_spending: number;
  daily_data: Array<{ date: string; amount: number }>;
}

export async function fetchDailySpendingTrend(days = 30) {
  return apiFetch<DailySpendingTrend>("analytics/daily-spending-trend", { query: { days } });
}

export async function fetchAIDashboard() {
  return apiFetch<AIDashboard>("ai/dashboard");
}

export async function fetchFinancialHealth() {
  return apiFetch<number | { score?: number; change?: number }>("ai/financial-health");
}
