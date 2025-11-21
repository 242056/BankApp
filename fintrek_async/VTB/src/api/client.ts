// Minimal API client wrapper with sensible defaults

export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

interface ApiOptions {
  method?: HttpMethod;
  headers?: Record<string, string>;
  body?: any;
  signal?: AbortSignal;
  auth?: boolean; // attach bearer token from localStorage if true (default true)
  query?: Record<string, string | number | boolean | undefined | null>;
}

const BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || "/api/v1";

function buildUrl(path: string, query?: ApiOptions["query"]) {
  const url = new URL(path.replace(/^\//, ""), ensureTrailingSlash(BASE_URL));
  if (query) {
    Object.entries(query).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, String(v));
    });
  }
  return url.toString();
}

function ensureTrailingSlash(u: string) {
  return u.endsWith("/") ? u : u + "/";
}

function getToken(): string | null {
  return (
    localStorage.getItem("access_token") ||
    localStorage.getItem("token") ||
    null
  );
}

async function refreshAccessToken(): Promise<string | null> {
  const rt = localStorage.getItem("refresh_token");
  if (!rt) return null;
  try {
    const url = buildUrl("auth/refresh");
    const res = await fetch(url, {
      method: "POST",
      headers: { "Accept": "application/json", "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: rt }),
    });
    const txt = await res.text();
    const json = safeJsonParse(txt) as any;
    if (!res.ok) throw new Error((json && (json.error || json.detail)) || "refresh failed");
    const at = json?.access_token;
    const newRt = json?.refresh_token;
    if (at) localStorage.setItem("access_token", at);
    if (newRt) localStorage.setItem("refresh_token", newRt);
    return at || null;
  } catch {
    // drop tokens on failure
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    return null;
  }
}

export async function apiFetch<T>(path: string, opts: ApiOptions = {}): Promise<T> {
  const { method = "GET", headers = {}, body, signal, auth = true, query } = opts;

  const init: RequestInit = {
    method,
    headers: {
      "Accept": "application/json",
      ...(body ? { "Content-Type": "application/json" } : {}),
      ...headers,
    },
    signal,
  };

  function attachAuth(h: Record<string,string>) {
    if (!auth) return;
    const token = getToken();
    if (token) h["Authorization"] = `Bearer ${token}`;
  }

  attachAuth(init.headers as Record<string,string>);

  if (body !== undefined) {
    init.body = typeof body === "string" ? body : JSON.stringify(body);
  }

  const url = buildUrl(path, query);
  let res = await fetch(url, init);

  // Attempt token refresh on 401 once
  if (auth && res.status === 401 && !path.startsWith("auth/") && localStorage.getItem("refresh_token")) {
    const newAt = await refreshAccessToken();
    if (newAt) {
      const retryInit: RequestInit = { ...init, headers: { ...(init.headers as any) } };
      (retryInit.headers as Record<string,string>)["Authorization"] = `Bearer ${newAt}`;
      res = await fetch(url, retryInit);
    }
  }

  const text = await res.text();
  const data = safeJsonParse(text);

  if (!res.ok) {
    const message = (data && (data.error || data.detail)) || res.statusText || "Request failed";
    const err = new Error(message) as Error & { status?: number; data?: unknown };
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data as T;
}

function safeJsonParse(text: string) {
  try { return text ? JSON.parse(text) : null; } catch { return text as unknown as any; }
}
