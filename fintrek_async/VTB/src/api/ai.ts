import { apiFetch } from "./client";

export interface RecommendationItem {
  id?: string;
  title?: string;
  description?: string;
  savingsPotential?: number;
  priority?: string;
  category?: string;
}

export interface RecommendationsResponse {
  recommendations: RecommendationItem[];
  count?: number;
}

export async function fetchRecommendations() {
  return apiFetch<RecommendationsResponse>("ai/recommendations");
}

export async function categorizeTransactions(limit = 100) {
  // Backend expects POST with Query param limit; body is not required
  return apiFetch<{ categorized_count: number; message: string }>("ai/categorize-transactions", {
    method: "POST",
    query: { limit },
  });
}

export async function forecastBalance(months = 6) {
  return apiFetch<{ months_ahead: number; forecast: Array<{ month?: string; value?: number } | number> }>("ai/forecast/balance", { query: { months } });
}

export async function fetchMonthlySpending(months = 6) {
  return apiFetch<{ months: number; data: Array<{ month: string; spending: number }> }>("ai/monthly-spending", { query: { months } });
}

export async function fetchRecurringPayments(minOccurrences = 3) {
  return apiFetch<{ recurring_payments: Array<{ name: string; amount: number; frequency: string }>; total_count: number; estimated_monthly_cost: number }>("ai/recurring-payments", { query: { min_occurrences: minOccurrences } });
}

export async function fetchAnomalies(threshold = 2.0) {
  return apiFetch<{ anomalies: Array<{ id: string; amount: number; date: string; category?: string; reason?: string }>; count: number }>("ai/anomalies", { query: { threshold } });
}

export async function fetchSpendingTrends() {
  return apiFetch<{ current_month: number; previous_month: number; change_percentage: number; trend: string }>("ai/spending-trends");
}

export async function fetchForecastSpending() {
  return apiFetch<{ spending: number; confidence: number; categories: Array<{ name: string; amount: number }> }>("ai/forecast/spending");
}

export async function fetchForecastIncome() {
  return apiFetch<{ income: number; confidence: number }>("ai/forecast/income");
}

export async function fetchProactiveAdvice(scenario: string) {
  return apiFetch<{ title: string; description: string; potential_savings: number; actions: Array<string> }>(`ai/proactive-advice/${scenario}`);
}
