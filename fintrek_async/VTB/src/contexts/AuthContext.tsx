import { createContext, useContext, useEffect, useMemo, useState } from "react";
import * as AuthAPI from "@/api/auth";

type AuthContextValue = {
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setTokens: (access: string, refresh?: string | null) => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(() => localStorage.getItem("access_token"));
  const [refreshToken, setRefreshToken] = useState<string | null>(() => localStorage.getItem("refresh_token"));

  const setTokens = (access: string, refresh?: string | null) => {
    setAccessToken(access);
    localStorage.setItem("access_token", access);
    if (typeof refresh !== "undefined") {
      setRefreshToken(refresh ?? null);
      if (refresh) localStorage.setItem("refresh_token", refresh);
      else localStorage.removeItem("refresh_token");
    }
  };

  const login = async (email: string, password: string) => {
    const res = await AuthAPI.login(email, password);
    setTokens(res.access_token, res.refresh_token);
  };

  const logout = () => {
    setAccessToken(null);
    setRefreshToken(null);
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  };

  const value = useMemo<AuthContextValue>(() => ({
    accessToken,
    refreshToken,
    isAuthenticated: Boolean(accessToken),
    login,
    logout,
    setTokens,
  }), [accessToken, refreshToken]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
