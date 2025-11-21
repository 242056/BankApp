import { apiFetch } from "./client";

export interface TransactionItem {
  id: string;
  date: string; // ISO
  type: "income" | "expense" | string;
  recipient?: string | null;
  category?: string | null;
  amount: number;
  bank?: string | null;
  merchant?: string | null;
}

export interface TransactionListResponse {
  transactions: TransactionItem[];
  total: number;
  page: number;
  page_size?: number;
}

export async function fetchTransactions(params: {
  page?: number;
  page_size?: number;
  account_id?: string;
  category_id?: string;
  date_from?: string;
  date_to?: string;
}) {
  return apiFetch<TransactionListResponse>("transactions", {
    query: params as any,
  });
}

export async function createTransaction(body: {
  account_id: string;
  transaction_type: "income" | "expense" | "transfer";
  amount: number;
  currency?: string;
  description?: string;
  merchant_name?: string;
  notes?: string;
  transaction_date: string; // ISO
  category_id?: string;
  related_account_id?: string;
}) {
  return apiFetch<any>("transactions", {
    method: "POST",
    body: { currency: "RUB", ...body },
  });
}

export async function updateTransaction(id: string, body: { category_id?: string; description?: string; notes?: string; status?: string; }) {
  return apiFetch<any>(`transactions/${id}`, {
    method: "PATCH",
    body,
  });
}
