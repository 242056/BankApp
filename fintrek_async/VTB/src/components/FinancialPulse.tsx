import { TrendingUp, TrendingDown } from "lucide-react";

interface FinancialPulseProps {
  score: number;
  trend: "up" | "down";
  change: number;
}

export const FinancialPulse = ({ score, trend, change }: FinancialPulseProps) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-accent";
    if (score >= 60) return "text-yellow-500";
    return "text-destructive";
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return "Отличное";
    if (score >= 60) return "Хорошее";
    if (score >= 40) return "Среднее";
    return "Требует внимания";
  };

  return (
    <div className="card-neo p-8 animate-scale-in">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-foreground">Финансовый пульс</h3>
        <div className="flex items-center gap-1 text-sm">
          {trend === "up" ? (
            <TrendingUp className="w-4 h-4 text-accent" />
          ) : (
            <TrendingDown className="w-4 h-4 text-destructive" />
          )}
          <span className={trend === "up" ? "text-accent" : "text-destructive"}>
            {change > 0 ? "+" : ""}{change}%
          </span>
        </div>
      </div>
      
      <div className="relative w-full h-48 flex items-center justify-center">
        <svg className="w-48 h-48 transform -rotate-90" viewBox="0 0 200 200">
          <circle
            cx="100"
            cy="100"
            r="80"
            fill="none"
            stroke="hsl(var(--muted))"
            strokeWidth="16"
          />
          <circle
            cx="100"
            cy="100"
            r="80"
            fill="none"
            stroke="hsl(var(--accent))"
            strokeWidth="16"
            strokeDasharray={`${(score / 100) * 502.4} 502.4`}
            strokeLinecap="round"
            className="transition-smooth"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-5xl font-bold ${getScoreColor(score)}`}>{score}</span>
          <span className="text-sm text-muted-foreground mt-1">{getScoreLabel(score)}</span>
        </div>
      </div>
      
      <p className="text-sm text-muted-foreground text-center mt-4">
        Ваше финансовое здоровье на основе доходов, расходов и инвестиций
      </p>
    </div>
  );
};
