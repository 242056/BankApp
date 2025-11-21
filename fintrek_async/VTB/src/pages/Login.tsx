import { useState } from "react";
import { useNavigate, Link, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import * as AuthAPI from "@/api/auth";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { LogIn } from "lucide-react";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation() as any;
  const { setTokens, isAuthenticated } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email || !password) {
      toast.error("Введите email и пароль");
      return;
    }
    try {
      setLoading(true);
      const res = await AuthAPI.login(email, password);
      setTokens(res.access_token, res.refresh_token);
      toast.success("Вход выполнен");
      const to = location?.state?.from?.pathname || "/dashboard";
      navigate(to, { replace: true });
    } catch (e: any) {
      toast.error(e?.message || "Не удалось войти");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container mx-auto px-4 max-w-md">
        <Card className="p-6 card-neo">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
            <LogIn className="w-8 h-8 text-accent" />
            Вход
          </h1>
          <p className="text-muted-foreground mb-6">Введите свои данные для доступа</p>
          <form onSubmit={onSubmit} className="space-y-4">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="you@example.com" value={email} onChange={(e)=>setEmail(e.target.value)} className="mt-2" disabled={loading} />
            </div>
            <div>
              <Label htmlFor="password">Пароль</Label>
              <Input id="password" type="password" placeholder="••••••••" value={password} onChange={(e)=>setPassword(e.target.value)} className="mt-2" disabled={loading} />
            </div>
            <Button type="submit" variant="accent" className="w-full" disabled={loading}>
              {loading ? "Входим..." : "Войти"}
            </Button>
          </form>
          <div className="text-sm text-muted-foreground mt-4">
            Нет аккаунта? <Link to="/register" className="text-accent underline">Зарегистрироваться</Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
