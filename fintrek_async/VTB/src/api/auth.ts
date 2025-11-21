import { apiFetch } from "./client";

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterBody {
  email: string;
  password: string;
  name: string;
}

export async function login(email: string, password: string) {
  // Backend expects application/x-www-form-urlencoded body
  const formData = new URLSearchParams();
  formData.append("email", email);
  formData.append("password", password);

  return apiFetch<TokenResponse>("auth/login", {
    method: "POST",
    auth: false,
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData.toString(),
  });
}

export async function register(body: RegisterBody) {
  return apiFetch<TokenResponse | any>("auth/register", {
    method: "POST",
    auth: false,
    body,
  });
}

export async function refresh(refresh_token: string) {
  return apiFetch<TokenResponse>("auth/refresh", {
    method: "POST",
    auth: false,
    body: { refresh_token },
  });
}
