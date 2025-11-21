import { Sparkles, X } from "lucide-react";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "./ui/button";
import iconAI from "@/assets/icon-ai.png";
import { fetchRecommendations } from "@/api/ai";

export const AIInsightPanel = () => {
  const [isOpen, setIsOpen] = useState(true);
  const { data, isLoading } = useQuery({ queryKey: ["ai-recommendations"], queryFn: fetchRecommendations });
  const insights = useMemo(() => data?.recommendations ?? [], [data]);

  if (!isOpen) {
    return (
      <Button
        onClick={() => setIsOpen(true)}
        variant="accent"
        size="icon"
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg z-50"
      >
        <Sparkles className="w-6 h-6" />
      </Button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 max-h-[600px] card-neo p-6 z-50 animate-slide-up overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <img src={iconAI} alt="AI" className="w-8 h-8" />
          <h3 className="font-semibold text-lg">AI Советник</h3>
        </div>
        <Button
          onClick={() => setIsOpen(false)}
          variant="ghost"
          size="icon"
          className="h-8 w-8"
        >
          <X className="w-4 h-4" />
        </Button>
      </div>

      <div className="space-y-3">
        {isLoading ? (
          <div className="p-4 rounded-xl border-2 animate-pulse bg-secondary" />
        ) : insights.length === 0 ? (
          <div className="text-sm text-muted-foreground">Пока нет рекомендаций</div>
        ) : (
          insights.map((insight: any) => {
            const type = (insight.priority || insight.category || "tip").toString().toLowerCase();
            const tone = type.includes("warn") ? "warning" : type.includes("opportunity") ? "opportunity" : "tip";
            return (
              <div
                key={insight.id || insight.title}
                className={`p-4 rounded-xl border-2 transition-smooth hover:shadow-md ${
                  tone === "opportunity"
                    ? "border-accent/30 bg-accent/5"
                    : tone === "warning"
                    ? "border-destructive/30 bg-destructive/5"
                    : "border-primary/30 bg-primary/5"
                }`}
              >
                <h4 className="font-semibold text-sm mb-1 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-accent" />
                  {insight.title || "Рекомендация"}
                </h4>
                <p className="text-xs text-muted-foreground">{insight.description || ""}</p>
              </div>
            );
          })
        )}
      </div>

      <Button variant="accent" className="w-full mt-4">
        Получить подробный анализ
      </Button>
    </div>
  );
};
