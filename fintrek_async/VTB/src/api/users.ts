import { apiFetch } from "./client";

export interface UserResponse {
  id: string;
  email: string;
  name: string;
  subscription_tier: string;
  created_at: string;
}

export interface UserUpdateBody {
  full_name?: string;
  email?: string;
  password?: string;
}

export async function fetchMe() {
  return apiFetch<UserResponse>("users/me");
}

export async function updateMe(body: UserUpdateBody) {
  return apiFetch<UserResponse>("users/me", {
    method: "PATCH",
    body,
  });
}
