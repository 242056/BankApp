import { apiFetch } from "./client";

export interface CategoryItem {
  id: string;
  name: string;
  category_type: string; // income | expense etc.
  is_system?: boolean;
  parent_id?: string | null;
}

export interface CategoryListResponse {
  categories: CategoryItem[];
  total: number;
}

export async function fetchCategories() {
  return apiFetch<CategoryListResponse>("categories");
}

export async function createCategory(body: { name: string; category_type: string; icon?: string; color?: string; parent_id?: string | null }) {
  return apiFetch<any>("categories", { method: "POST", body });
}

export async function updateCategory(id: string, body: { name?: string; category_type?: string; icon?: string; color?: string; parent_id?: string | null }) {
  return apiFetch<any>(`categories/${id}`, { method: "PATCH", body });
}

export async function deleteCategory(id: string) {
  return apiFetch<void>(`categories/${id}`, { method: "DELETE" });
}
