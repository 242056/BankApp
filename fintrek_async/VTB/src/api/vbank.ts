import { apiFetch } from "./client";

export async function vbankSyncAccounts() {
  return apiFetch<any>("vbank/sync-accounts", { method: "POST" });
}

export async function vbankSyncTransactions(account_id: string, date_from?: string, date_to?: string) {
  return apiFetch<any>("vbank/sync-transactions", { method: "POST", query: { account_id, date_from, date_to } });
}
