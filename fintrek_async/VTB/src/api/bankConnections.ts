import { apiFetch } from "./client";

export interface BankConnectionItem {
  id: string;
  bank_name: string;
  bank_bic?: string;
  status: string; // ACTIVE | DISCONNECTED
  created_at?: string;
}

export interface BankConnectionListResponse {
  connections: BankConnectionItem[];
  total: number;
}

export async function fetchBankConnections() {
  return apiFetch<BankConnectionListResponse>("bank-connections");
}

export async function createBankConnection(body: { bank_name: string; bank_bic?: string }) {
  return apiFetch<BankConnectionItem>("bank-connections", { method: "POST", body });
}

export async function deleteBankConnection(id: string) {
  return apiFetch<void>(`bank-connections/${id}`, { method: "DELETE" });
}

export async function syncBankConnection(connection_id: string) {
  return apiFetch<any>("bank-connections/sync", { method: "POST", body: { connection_id } });
}
