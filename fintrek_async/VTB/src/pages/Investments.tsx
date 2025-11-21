import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TrendingUp, Leaf, PieChart as PieChartIcon, RefreshCw } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, AreaChart, Area, XAxis, YAxis, CartesianGrid } from "recharts";

const portfolioData: Array<{ name: string; value: number; color: string; percentage: number }> = [];
const performanceData: Array<{ month: string; value: number }> = [];
const holdings: Array<{ name: string; ticker: string; shares?: number; price: number; change: number; esg: number }> = [];

export default function Investments() {
  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container mx-auto px-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
              <TrendingUp className="w-10 h-10 text-accent" />
              Инвестиции
            </h1>
            <p className="text-muted-foreground">Управление портфелем и ESG-анализ</p>
          </div>
          
          <Button variant="accent" className="gap-2">
            <RefreshCw className="w-4 h-4" />
            Ребалансировка
          </Button>
        </div>

        {/* Summary Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-6">
          <Card className="p-6 card-neo">
            <p className="text-sm text-muted-foreground mb-2">Всего активов</p>
            <p className="text-3xl font-bold text-accent">₽580,000</p>
            <p className="text-sm text-accent mt-1">+16% за год</p>
          </Card>
          <Card className="p-6 card-neo">
            <p className="text-sm text-muted-foreground mb-2">Доходность</p>
            <p className="text-3xl font-bold text-accent">+8.5%</p>
            <p className="text-sm text-muted-foreground mt-1">За последний год</p>
          </Card>
          <Card className="p-6 card-neo">
            <p className="text-sm text-muted-foreground mb-2">ESG Score</p>
            <p className="text-3xl font-bold text-accent flex items-center gap-2">
              78
              <Leaf className="w-6 h-6" />
            </p>
            <p className="text-sm text-muted-foreground mt-1">Выше среднего</p>
          </Card>
          <Card className="p-6 card-neo">
            <p className="text-sm text-muted-foreground mb-2">Дивиденды</p>
            <p className="text-3xl font-bold text-primary">₽12,400</p>
            <p className="text-sm text-muted-foreground mt-1">В этом году</p>
          </Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          {/* Portfolio Distribution */}
          <Card className="p-6 card-neo">
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <PieChartIcon className="w-5 h-5 text-accent" />
              Диверсификация портфеля
            </h3>
            {portfolioData.length === 0 ? (
              <div className="text-sm text-muted-foreground">Нет данных (эндпоинтов для инвестиций нет)</div>
            ) : (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={portfolioData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percentage }) => `${name} ${percentage}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {portfolioData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "0.5rem",
                  }}
                  formatter={(value: number) => `₽${value.toLocaleString()}`}
                />
              </PieChart>
            </ResponsiveContainer>
            )}
            {portfolioData.length > 0 && (
              <div className="grid grid-cols-2 gap-3 mt-4">
                {portfolioData.map((item, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-sm">{item.name}: ₽{item.value.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Performance */}
          <Card className="p-6 card-neo">
            <h3 className="text-xl font-semibold mb-4">Динамика роста</h3>
            {performanceData.length === 0 ? (
              <div className="text-sm text-muted-foreground">Нет данных</div>
            ) : (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={performanceData}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(175 100% 39%)" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="hsl(175 100% 39%)" stopOpacity={0} />
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
                  formatter={(value: number) => `₽${value.toLocaleString()}`}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="hsl(175 100% 39%)"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorValue)"
                />
              </AreaChart>
            </ResponsiveContainer>
            )}
          </Card>
        </div>

        {/* Holdings Table */}
        <Card className="p-6 card-neo">
          <h3 className="text-xl font-semibold mb-4">Активы в портфеле</h3>
          <div className="overflow-x-auto">
            {holdings.length === 0 ? (
              <div className="text-sm text-muted-foreground p-4">Нет данных</div>
            ) : (
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">Актив</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">Тикер</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Кол-во</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Цена</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Изменение</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-muted-foreground">ESG Score</th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((holding, index) => (
                  <tr key={index} className="border-b border-border/50 hover:bg-secondary/50 transition-smooth">
                    <td className="py-3 px-4 font-medium">{holding.name}</td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-mono bg-secondary">
                        {holding.ticker}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right text-sm">{holding.shares}</td>
                    <td className="py-3 px-4 text-right text-sm font-semibold">₽{holding.price.toLocaleString()}</td>
                    <td className={`py-3 px-4 text-right text-sm font-semibold ${
                      holding.change >= 0 ? "text-accent" : "text-destructive"
                    }`}>
                      {holding.change > 0 ? "+" : ""}{holding.change}%
                    </td>
                    <td className="py-3 px-4 text-center">
                      <div className="flex items-center justify-center gap-1">
                        <span className={`font-semibold ${
                          holding.esg >= 80 ? "text-accent" : holding.esg >= 70 ? "text-yellow-500" : "text-muted-foreground"
                        }`}>
                          {holding.esg}
                        </span>
                        {holding.esg >= 75 && <Leaf className="w-4 h-4 text-accent" />}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            )}
          </div>

          <div className="mt-6 p-4 rounded-xl bg-accent/5 border border-accent/20">
            <div className="flex items-start gap-3">
              <Leaf className="w-5 h-5 text-accent mt-0.5" />
              <div>
                <p className="font-semibold text-sm mb-1">ESG Рекомендация</p>
                <p className="text-sm text-muted-foreground">
                  Ваш портфель имеет хороший ESG-рейтинг. Рекомендуем добавить зелёные облигации для улучшения экологической составляющей.
                </p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
