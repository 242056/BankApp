import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { forecastBalance } from "@/api/ai";
import { Calculator, TrendingDown, AlertCircle } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Area, AreaChart } from "recharts";

const scenarios = [
  { id: "vacation", name: "Отпуск", icon: "✈️" },
  { id: "car", name: "Покупка авто", icon: "🚗" },
  { id: "apartment", name: "Квартира", icon: "🏠" },
  { id: "education", name: "Образование", icon: "🎓" },
];

export default function Planner() {
  const [selectedScenario, setSelectedScenario] = useState("vacation");
  const [amount, setAmount] = useState([200000]);
  const [months, setMonths] = useState([12]);

  const generateProjection = () => {
    const monthlyPayment = amount[0] / months[0];
    const currentSavings = 350000;
    
    return Array.from({ length: months[0] + 1 }, (_, i) => ({
      month: i,
      balance: currentSavings - (monthlyPayment * i),
      target: currentSavings - amount[0],
      income: 150000,
      expenses: 94000 + monthlyPayment,
    }));
  };

  const projectionData = generateProjection();
  const finalBalance = projectionData[projectionData.length - 1].balance;
  const isAffordable = finalBalance >= 0;

  const { data: balanceForecast } = useQuery({
    queryKey: ["ai-forecast-balance", months[0]],
    queryFn: () => forecastBalance(months[0]),
  });

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
            <Calculator className="w-10 h-10 text-accent" />
            Планировщик "Что если?"
          </h1>
          <p className="text-muted-foreground">Моделируйте финансовые сценарии и планируйте крупные покупки</p>
        </div>

        {/* Scenario Selection */}
        <div className="grid md:grid-cols-4 gap-4 mb-6">
          {scenarios.map((scenario) => (
            <button
              key={scenario.id}
              onClick={() => setSelectedScenario(scenario.id)}
              className={`card-neo p-6 text-center transition-smooth hover:shadow-lg ${
                selectedScenario === scenario.id ? "ring-2 ring-accent" : ""
              }`}
            >
              <div className="text-4xl mb-2">{scenario.icon}</div>
              <p className="font-semibold">{scenario.name}</p>
            </button>
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          {/* Controls */}
          <Card className="p-6 card-neo">
            <h3 className="text-xl font-semibold mb-6">Параметры сценария</h3>
            
            <div className="space-y-6">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Сумма покупки: ₽{amount[0].toLocaleString()}
                </label>
                <Slider
                  value={amount}
                  onValueChange={setAmount}
                  max={2000000}
                  min={50000}
                  step={10000}
                  className="my-4"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">
                  Период накопления: {months[0]} мес.
                </label>
                <Slider
                  value={months}
                  onValueChange={setMonths}
                  max={36}
                  min={3}
                  step={1}
                  className="my-4"
                />
              </div>

              <div className="pt-4 border-t border-border">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-muted-foreground">Ежемесячный платёж:</span>
                  <span className="font-semibold text-lg">₽{(amount[0] / months[0]).toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-muted-foreground">Текущие сбережения:</span>
                  <span className="font-semibold text-lg text-accent">₽350,000</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Итоговый баланс:</span>
                  <span className={`font-semibold text-lg ${isAffordable ? "text-accent" : "text-destructive"}`}>
                    ₽{Math.abs(finalBalance).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </Card>

          {/* Impact Summary */}
          <Card className="p-6 card-neo">
            <h3 className="text-xl font-semibold mb-6">Влияние на бюджет</h3>
            
            {!isAffordable && (
              <div className="mb-4 p-4 rounded-xl bg-destructive/10 border border-destructive/30 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-destructive mt-0.5" />
                <div>
                  <p className="font-semibold text-sm text-destructive mb-1">Внимание!</p>
                  <p className="text-xs text-muted-foreground">
                    При текущих параметрах сбережения будут исчерпаны. Рекомендуем увеличить период накопления.
                  </p>
                </div>
              </div>
            )}

            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-accent/5 border border-accent/20">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingDown className="w-5 h-5 text-accent" />
                  <p className="font-semibold">Доступный бюджет</p>
                </div>
                <p className="text-2xl font-bold text-accent">
                  ₽{(150000 - 94000 - (amount[0] / months[0])).toLocaleString()}
                </p>
                <p className="text-sm text-muted-foreground mt-1">В месяц после всех расходов</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-secondary">
                  <p className="text-sm text-muted-foreground mb-1">Доход</p>
                  <p className="text-xl font-bold">₽150,000</p>
                </div>
                <div className="p-4 rounded-xl bg-secondary">
                  <p className="text-sm text-muted-foreground mb-1">Расходы</p>
                  <p className="text-xl font-bold">₽{(94000 + (amount[0] / months[0])).toLocaleString()}</p>
                </div>
              </div>
            </div>

            <Button variant="accent" className="w-full mt-6">
              Сохранить план
            </Button>
          </Card>
        </div>

        {/* Projection Chart */}
        <Card className="p-6 card-neo">
          <h3 className="text-xl font-semibold mb-4">Прогноз баланса</h3>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={projectionData}>
              <defs>
                <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(175 100% 39%)" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="hsl(175 100% 39%)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="month"
                stroke="hsl(var(--muted-foreground))"
                label={{ value: "Месяцы", position: "insideBottom", offset: -5 }}
              />
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
                dataKey="balance"
                stroke="hsl(175 100% 39%)"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorBalance)"
                name="Баланс"
              />
              <Line
                type="monotone"
                dataKey="target"
                stroke="hsl(0 84% 60%)"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="Целевой баланс"
              />
              {balanceForecast?.forecast && (
                <Line
                  type="monotone"
                  data={projectionData.map((p, i) => ({ ...p, forecast: Number((balanceForecast.forecast as any[])[i] ?? p.balance) }))}
                  dataKey="forecast"
                  stroke="hsl(215 76% 16%)"
                  strokeWidth={2}
                  dot={false}
                  name="Прогноз AI"
                />
              )}
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  );
}
