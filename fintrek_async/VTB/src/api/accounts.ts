import { apiFetch } from "./client";

export interface AccountItem {
  id: string;
  account_name: string;
  account_type: string;
  currency: string;
  balance: number;
  account_number?: string | null;
}

export interface AccountListResponse {
  accounts: AccountItem[];
  total: number;
}

export async function fetchAccounts() {
  // Backend path: GET /accounts/
  return apiFetch<AccountListResponse>("accounts/");
}

export async function createAccount(body: { account_name: string; account_type: string; currency?: string; balance?: number; account_number?: string }) {
  return apiFetch<any>("accounts/", { method: "POST", body: { currency: "RUB", balance: 0, ...body } });
}

export async function updateAccount(id: string, body: { account_name?: string; balance?: number; status?: string }) {
  return apiFetch<any>(`accounts/${id}`, { method: "PATCH", body });
}

export async function deleteAccount(id: string) {
  return apiFetch<void>(`accounts/${id}`, { method: "DELETE" });
}
