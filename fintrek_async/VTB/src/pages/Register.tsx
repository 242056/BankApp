import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import * as AuthAPI from "@/api/auth";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { UserPlus } from "lucide-react";

export default function Register() {
  const navigate = useNavigate();
  const { setTokens } = useAuth();
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email || !password || !name) {
      toast.error("Заполните имя, email и пароль");
      return;
    }
    try {
      setLoading(true);
      await AuthAPI.register({ email, password, name });
      // Бэкенд на /auth/register не возвращает токены — логинимся сразу после регистрации
      const res = await AuthAPI.login(email, password);
      setTokens(res.access_token, res.refresh_token);
      toast.success("Регистрация выполнена");
      navigate("/dashboard");
    } catch (e: any) {
      toast.error(e?.message || "Не удалось зарегистрироваться");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container mx-auto px-4 max-w-md">
        <Card className="p-6 card-neo">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
            <UserPlus className="w-8 h-8 text-accent" />
            Регистрация
          </h1>
          <p className="text-muted-foreground mb-6">Создайте новый аккаунт</p>
          <form onSubmit={onSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name">Имя</Label>
              <Input id="name" placeholder="Иван Иванов" value={name} onChange={(e)=>setName(e.target.value)} className="mt-2" disabled={loading} />
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="you@example.com" value={email} onChange={(e)=>setEmail(e.target.value)} className="mt-2" disabled={loading} />
            </div>
            <div>
              <Label htmlFor="password">Пароль</Label>
              <Input id="password" type="password" placeholder="Минимум 8 символов" value={password} onChange={(e)=>setPassword(e.target.value)} className="mt-2" disabled={loading} />
            </div>
            <Button type="submit" variant="accent" className="w-full" disabled={loading}>
              {loading ? "Создаём..." : "Зарегистрироваться"}
            </Button>
          </form>
          <div className="text-sm text-muted-foreground mt-4">
            Уже есть аккаунт? <Link to="/login" className="text-accent underline">Войти</Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
