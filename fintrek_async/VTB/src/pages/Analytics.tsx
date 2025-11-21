import { useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, Filter, Calendar, Wand2 } from "lucide-react";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { fetchIncomeVsExpenses, fetchSpendingByCategory, fetchTransactionStatistics, fetchDailySpendingTrend } from "@/api/analytics";
import { fetchTransactions, deleteTransaction } from "@/api/transactions";
import { fetchCategories } from "@/api/categories";
import { categorizeTransactions } from "@/api/ai";
import { toast } from "sonner";

function monthLabel(ym: string) {
  const m = Number(ym.split("-")[1]);
  const ru = ["Янв","Фев","Мар","Апр","Май","Июн","Июл","Авг","Сен","Окт","Ноя","Дек"]; 
  return ru[(m - 1 + 12) % 12] || ym;
}

function AIButtons({ qcKeyTx }: { qcKeyTx: any[] }) {
  const qc = useQueryClient();
  const categorizeMut = useMutation({
    mutationFn: () => categorizeTransactions(100),
    onSuccess: (res: any) => { toast.success(res?.message || "Категоризация выполнена"); qc.invalidateQueries({ queryKey: qcKeyTx }); },
    onError: (e: any) => toast.error(e?.message || "Ошибка категоризации"),
  });
  return (
    <Button variant="accent" onClick={()=>categorizeMut.mutate()} disabled={categorizeMut.isPending}>
      {categorizeMut.isPending ? "Обработка..." : "Автокатегоризация"}
    </Button>
  );
}

export default function Analytics() {
  const qc = useQueryClient();
  const { data: ive, isLoading: loadingIve } = useQuery({ queryKey: ["income-vs-expenses", 6], queryFn: () => fetchIncomeVsExpenses(6), onError: () => toast.error("Не удалось загрузить тренд") });
  const { data: stats, isLoading: loadingStats } = useQuery({ queryKey: ["transaction-statistics", 30], queryFn: () => fetchTransactionStatistics(30), onError: () => toast.error("Не удалось загрузить статистику") });
  const { data: spendCat, isLoading: loadingCat } = useQuery({ queryKey: ["spending-by-category", { days: 30 }], queryFn: () => fetchSpendingByCategory(), onError: () => toast.error("Не удалось загрузить категории") });
  const { data: txList, isLoading: loadingTx } = useQuery({ queryKey: ["transactions", 1], queryFn: () => fetchTransactions({ page: 1, page_size: 10 }), onError: () => toast.error("Не удалось загрузить операции") });
  const { data: catList } = useQuery({ queryKey: ["categories"], queryFn: fetchCategories });
  const catMap = useMemo(() => {
    const m = new Map<string,string>();
    catList?.categories?.forEach(c => m.set(c.id, c.name));
    return m;
  }, [catList]);

  const summary = useMemo(() => {
    const totalExpenses = Number(stats?.expenses?.total ?? 0);
    const avgCheck = Number(stats?.expenses?.average ?? 0);
    const top = spendCat?.categories?.slice()?.sort((a,b) => (b.total - a.total))[0];
    const topName = top?.category ?? "—";
    const topTotal = Number(top?.total ?? 0);
    const topPct = Number(top?.percentage ?? 0);
    return { totalExpenses, avgCheck, topName, topTotal, topPct };
  }, [stats, spendCat]);

  const trendData = useMemo(() => {
    if (!ive?.data?.length) return [] as Array<{ month: string; value: number }>;
    return ive.data.map((m) => ({ month: monthLabel(m.month), value: m.expenses ?? 0 }));
  }, [ive]);

  const transactions = useMemo(() => {
    if (!txList?.transactions?.length) return [] as Array<{ date: string; category: string; merchant: string; amount: number; type: string }>;
    return txList.transactions.map((t) => {
      const categoryId = (t as any).category_id ?? (t as any).categoryId;
      const category = catMap.get(String(categoryId)) || (t as any).category || "—";
      return {
        date: (t as any).transaction_date ?? (t as any).date ?? "",
        category,
        merchant: (t as any).merchant_name ?? (t as any).merchant ?? "",
        amount: Number((t as any).amount ?? 0),
        type: ((t as any).transaction_type ?? (t as any).type ?? "expense").toLowerCase(),
      };
    });
  }, [txList, catMap]);

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container mx-auto px-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Аналитика бюджета</h1>
            <p className="text-muted-foreground">Детальный анализ ваших финансов</p>
          </div>
          
          <div className="flex gap-2">
            <Button variant="outline" className="gap-2">
              <Filter className="w-4 h-4" />
              Фильтры
            </Button>
            <Button variant="outline" className="gap-2">
              <Calendar className="w-4 h-4" />
              Период
            </Button>
            <Button variant="accent" className="gap-2">
              <Download className="w-4 h-4" />
              Экспорт
            </Button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-6">
          <Card className="p-6 card-neo">
            <p className="text-sm text-muted-foreground mb-2">Общие расходы</p>
            <p className={`text-3xl font-bold text-primary ${loadingStats ? "animate-pulse" : ""}`}>₽{summary.totalExpenses.toLocaleString()}</p>
            <p className="text-sm text-accent mt-1">&nbsp;</p>
          </Card>
          <Card className="p-6 card-neo">
            <p className="text-sm text-muted-foreground mb-2">Средний чек</p>
            <p className={`text-3xl font-bold text-primary ${loadingStats ? "animate-pulse" : ""}`}>₽{summary.avgCheck.toLocaleString()}</p>
            <p className="text-sm text-muted-foreground mt-1">За последний период</p>
          </Card>
          <Card className="p-6 card-neo">
            <p className="text-sm text-muted-foreground mb-2">Топ категория</p>
            <p className={`text-3xl font-bold text-accent ${loadingCat ? "animate-pulse" : ""}`}>{summary.topName}</p>
            <p className="text-sm text-muted-foreground mt-1">₽{summary.topTotal.toLocaleString()} ({summary.topPct}%)</p>
          </Card>
        </div>

        {/* AI Tools */}
        <Card className="p-6 card-neo mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold mb-1 flex items-center gap-2"><Wand2 className="w-5 h-5 text-accent"/> AI инструменты</h3>
              <p className="text-sm text-muted-foreground">Автокатегоризация некатегоризированных транзакций</p>
            </div>
            <AIButtons qcKeyTx={["transactions"]} />
          </div>
        </Card>

        {/* Charts */}
        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          <Card className="p-6 card-neo">
            <h3 className="text-xl font-semibold mb-4">Расходы по категориям</h3>
            <div className="text-sm text-muted-foreground">Недоступно (нет соответствующего API)</div>
          </Card>

          <Card className="p-6 card-neo">
            <h3 className="text-xl font-semibold mb-4">Тренд расходов</h3>
            <ResponsiveContainer width="100%" height={350}>
              {loadingIve ? (
                <div className="h-[350px] w-full animate-pulse rounded-xl bg-secondary" />
              ) : trendData.length ? (
                <LineChart data={trendData}>
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
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="hsl(175 100% 39%)"
                  strokeWidth={3}
                  dot={{ fill: "hsl(175 100% 39%)", r: 6 }}
                  activeDot={{ r: 8 }}
                />
              </LineChart>
            ) : (
              <div className="text-sm text-muted-foreground">Нет данных</div>
            )}
            </ResponsiveContainer>
          </Card>
        </div>

        {/* Transactions Table */}
        <Card className="p-6 card-neo">
          <h3 className="text-xl font-semibold mb-4">Последние транзакции</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">Дата</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">Категория</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">Получатель</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Сумма</th>
                </tr>
              </thead>
              <tbody>
                {loadingTx ? (
                  <tr>
                    <td colSpan={4} className="py-6 text-center text-sm text-muted-foreground">Загрузка...</td>
                  </tr>
                ) : transactions.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="py-6 text-center text-sm text-muted-foreground">Нет операций</td>
                  </tr>
                ) : (
                  transactions.map((transaction, index) => (
                    <tr key={index} className="border-b border-border/50 hover:bg-secondary/50 transition-smooth">
                      <td className="py-3 px-4 text-sm">{String(transaction.date).slice(0,10)}</td>
                      <td className="py-3 px-4">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-accent/10 text-accent">
                          {transaction.category}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm">{transaction.merchant}</td>
                      <td className={`py-3 px-4 text-sm text-right font-semibold ${
                        transaction.type === "income" ? "text-accent" : "text-foreground"
                      }`}>
                        {transaction.amount > 0 ? "+" : ""}₽{transaction.amount.toLocaleString()}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}
