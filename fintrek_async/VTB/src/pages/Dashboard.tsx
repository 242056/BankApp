import { useMemo, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { FinancialPulse } from "@/components/FinancialPulse";
import { AIInsightPanel } from "@/components/AIInsightPanel";
import { Card } from "@/components/ui/card";
import { Wallet, TrendingUp, CreditCard, PiggyBank } from "lucide-react";
import { AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { fetchAccountSummary, fetchIncomeVsExpenses, fetchSpendingByCategory, fetchAIDashboard, fetchFinancialHealth } from "@/api/analytics";
import { toast } from "sonner";
import { CreateAccountDialog } from "@/components/CreateAccountDialog";

function monthLabel(ym: string) {
  // ym is like "2024-06"
  const m = Number(ym.split("-")[1]);
  const ru = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]; // keep UI style
  return ru[(m - 1 + 12) % 12] || ym;
}

export default function Dashboard() {
  const { data: accountSummary, isLoading: loadingAcc, isError: isAccError } = useQuery({
    queryKey: ["account-summary"],
    queryFn: fetchAccountSummary,
  });

  const { data: ive, isLoading: loadingIve, isError: isIveError } = useQuery({
    queryKey: ["income-vs-expenses", 6],
    queryFn: () => fetchIncomeVsExpenses(6),
  });

  const { data: spendCat, isLoading: loadingSpend, isError: isSpendError } = useQuery({
    queryKey: ["spending-by-category", { days: 30 }],
    queryFn: () => fetchSpendingByCategory(),
  });

  const { data: aiDash, isLoading: loadingAi } = useQuery({
    queryKey: ["ai-dashboard"],
    queryFn: fetchAIDashboard,
  });

  const { data: finHealth, isLoading: loadingFin } = useQuery({
    queryKey: ["financial-health"],
    queryFn: fetchFinancialHealth,
    enabled: !aiDash, // only if dashboard not available
  });

  useEffect(() => {
    if (isAccError) toast.error("Не удалось загрузить счета");
    if (isIveError) toast.error("Не удалось загрузить доходы и расходы");
    if (isSpendError) toast.error("Не удалось загрузить категории расходов");
  }, [isAccError, isIveError, isSpendError]);

  const accountsUI = useMemo(() => {
    const accs = (accountSummary as any)?.accounts || [];
    if (!accs.length) return [];
    const colorByType: Record<string, string> = {
      checking: "hsl(175 100% 39%)",
      savings: "hsl(215 76% 16%)",
      investment: "hsl(175 80% 50%)",
      credit: "hsl(0 84% 60%)",
    };
    const iconByType: Record<string, any> = {
      checking: Wallet,
      savings: PiggyBank,
      investment: TrendingUp,
      credit: CreditCard,
    };
    return accs.map((a: any) => ({
      name: a.name,
      amount: a.balance,
      icon: iconByType[a.type] ?? Wallet,
      color: colorByType[a.type] ?? "hsl(215 20% 93%)",
    }));
  }, [accountSummary]);

  const incomeExpenseUI = useMemo(() => {
    const data = (ive as any)?.data || [];
    if (!data.length) return [];
    return data.map((p: any) => ({
      month: monthLabel(p.month),
      income: p.income ?? 0,
      expenses: p.expenses ?? 0,
    }));
  }, [ive]);

  const categoryUI = useMemo(() => {
    const cats = (spendCat as any)?.categories || [];
    if (!cats.length) return [];
    const palette = [
      "hsl(175 100% 39%)",
      "hsl(215 76% 16%)",
      "hsl(175 80% 50%)",
      "hsl(215 60% 25%)",
      "hsl(215 20% 93%)",
    ];
    return cats.map((c: any, i: number) => ({
      name: c.category,
      value: c.total,
      color: palette[i % palette.length],
    }));
  }, [spendCat]);

  const pulse = useMemo(() => {
    // Derive score/trend/change from aiDash or finHealth; fall back to constants to preserve UI
    let score = 78, change = 5, trend: "up" | "down" = "up";
    const fh = (aiDash as any)?.financial_health ?? finHealth;
    if (typeof fh === "number") {
      score = Math.max(0, Math.min(100, Math.round(fh)));
    } else if (fh && typeof fh === "object") {
      if (typeof fh.score === "number") score = fh.score;
      if (typeof fh.change === "number") { change = Math.abs(fh.change); trend = fh.change >= 0 ? "up" : "down"; }
    }
    return { score, change, trend };
  }, [aiDash, finHealth]);

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container mx-auto px-4">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">Добро пожаловать!</h1>
            <p className="text-muted-foreground">Вот обзор ваших финансов</p>
          </div>
          <CreateAccountDialog />
        </div>

        <div className="grid lg:grid-cols-3 gap-6 mb-6">
          {/* Financial Pulse */}
          <div className={`lg:col-span-1 ${loadingAi || loadingFin ? "animate-pulse opacity-60" : ""}`}>
            <FinancialPulse score={pulse.score} trend={pulse.trend} change={pulse.change} />
          </div>

          {/* Accounts Summary */}
          <div className="lg:col-span-2 grid sm:grid-cols-2 gap-4">
            {loadingAcc ? (
              <>
                <Card className="p-6 card-neo animate-pulse h-28" />
                <Card className="p-6 card-neo animate-pulse h-28" />
              </>
            ) : accountsUI.length ? (
              accountsUI.map((account: any, index: number) => (
                <Card
                  key={index}
                  className="p-6 card-neo hover:shadow-lg transition-smooth animate-scale-in"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <div className="flex items-center justify-between mb-4">
                    <account.icon className="w-8 h-8" style={{ color: account.color }} />
                    <span className="text-sm text-muted-foreground">{account.name}</span>
                  </div>
                  <div className="text-2xl font-bold" style={{ color: account.color }}>
                    {account.amount >= 0 ? "₽" : "-₽"}
                    {Math.abs(account.amount).toLocaleString()}
                  </div>
                </Card>
              ))
            ) : (
              <Card className="p-6 card-neo">
                <div className="text-sm text-muted-foreground">Нет счетов</div>
              </Card>
            )}
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          {/* Income vs Expenses */}
          <Card className="p-6 card-neo">
            <h3 className="text-xl font-semibold mb-4">Доходы и расходы</h3>
            {loadingIve ? (
              <div className="h-[300px] w-full animate-pulse rounded-xl bg-secondary" />
            ) : incomeExpenseUI.length ? (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={incomeExpenseUI}>
                  <defs>
                    <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(175 100% 39%)" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="hsl(175 100% 39%)" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorExpenses" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(215 76% 16%)" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="hsl(215 76% 16%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" />
                  <YAxis stroke="hsl(var(--muted-foreground))" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "0.5rem",
                    }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="income"
                    stroke="hsl(175 100% 39%)"
                    fillOpacity={1}
                    fill="url(#colorIncome)"
                    name="Доходы"
                  />
                  <Area
                    type="monotone"
                    dataKey="expenses"
                    stroke="hsl(215 76% 16%)"
                    fillOpacity={1}
                    fill="url(#colorExpenses)"
                    name="Расходы"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-sm text-muted-foreground">Нет данных</div>
            )}
          </Card>

          {/* Category Breakdown */}
          <Card className="p-6 card-neo">
            <h3 className="text-xl font-semibold mb-4">Расходы по категориям</h3>
            {loadingSpend ? (
              <div className="h-[300px] w-full animate-pulse rounded-xl bg-secondary" />
            ) : categoryUI.length ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={categoryUI}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {categoryUI.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "0.5rem",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-sm text-muted-foreground">Нет данных</div>
            )}
          </Card>
        </div>

        {/* Monthly Comparison */}
        <Card className="p-6 card-neo">
          <h3 className="text-xl font-semibold mb-4">Сравнение по месяцам</h3>
          {loadingIve ? (
            <div className="h-[300px] w-full animate-pulse rounded-xl bg-secondary" />
          ) : incomeExpenseUI.length ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={incomeExpenseUI}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "0.5rem",
                  }}
                />
                <Legend />
                <Bar dataKey="income" fill="hsl(175 100% 39%)" name="Доходы" radius={[8, 8, 0, 0]} />
                <Bar dataKey="expenses" fill="hsl(215 76% 16%)" name="Расходы" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-sm text-muted-foreground">Нет данных</div>
          )}
        </Card>
      </div>

      <AIInsightPanel />
    </div>
  );
}
