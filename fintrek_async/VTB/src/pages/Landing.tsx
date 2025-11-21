import { Button } from "@/components/ui/button";
import { ArrowRight, Shield, Zap, Brain, TrendingUp } from "lucide-react";
import { Link } from "react-router-dom";
import heroImage from "@/assets/hero-finance.jpg";
import iconGrowth from "@/assets/icon-growth.png";
import iconAI from "@/assets/icon-ai.png";

const features = [
  {
    icon: Brain,
    title: "AI Советник",
    description: "Умная аналитика и персональные рекомендации на основе ваших финансов",
  },
  {
    icon: TrendingUp,
    title: "Инвестиции",
    description: "Отслеживание портфеля, ESG-скоринг и автоматическая ребалансировка",
  },
  {
    icon: Shield,
    title: "Безопасность",
    description: "Банковский уровень защиты данных и интеграция с VTB Open API",
  },
  {
    icon: Zap,
    title: "Автоматизация",
    description: "Умная категоризация транзакций и планирование бюджета",
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden gradient-subtle">
        <div className="absolute inset-0 opacity-10">
          <img src={heroImage} alt="" className="w-full h-full object-cover" />
        </div>
        
        <div className="container mx-auto px-4 py-24 relative">
          <div className="max-w-4xl mx-auto text-center animate-fade-in">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/10 border border-accent/30 mb-6">
              <Zap className="w-4 h-4 text-accent" />
              <span className="text-sm font-medium text-accent">Powered by VTB Open API</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              Ваш умный финансовый
              <span className="block gradient-accent bg-clip-text text-transparent">
                советник
              </span>
            </h1>
            
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Управляйте финансами с помощью AI. Анализируйте расходы, планируйте будущее 
              и принимайте взвешенные инвестиционные решения.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/dashboard">
                <Button variant="hero" size="lg" className="gap-2">
                  Начать бесплатно
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </Link>
              <Link to="/pricing">
                <Button variant="outline" size="lg">
                  Посмотреть тарифы
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16 animate-slide-up">
            <h2 className="text-4xl font-bold mb-4">Возможности платформы</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Все инструменты для полного контроля над вашими финансами
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <div
                key={index}
                className="card-neo p-6 hover:shadow-lg transition-smooth animate-scale-in"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="gradient-accent w-12 h-12 rounded-2xl flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-accent-foreground" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-24 gradient-primary">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-12 text-center text-primary-foreground">
            <div className="animate-fade-in">
              <div className="flex justify-center mb-4">
                <img src={iconGrowth} alt="Growth" className="w-16 h-16 opacity-90" />
              </div>
              <div className="text-5xl font-bold mb-2">10K+</div>
              <div className="text-lg opacity-90">Активных пользователей</div>
            </div>
            <div className="animate-fade-in" style={{ animationDelay: "100ms" }}>
              <div className="flex justify-center mb-4">
                <img src={iconAI} alt="AI" className="w-16 h-16 opacity-90" />
              </div>
              <div className="text-5xl font-bold mb-2">1M+</div>
              <div className="text-lg opacity-90">Проанализировано транзакций</div>
            </div>
            <div className="animate-fade-in" style={{ animationDelay: "200ms" }}>
              <div className="text-5xl font-bold mb-2">₽2.5B</div>
              <div className="text-lg opacity-90">Средств под управлением</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-background">
        <div className="container mx-auto px-4">
          <div className="card-neo max-w-4xl mx-auto p-12 text-center">
            <h2 className="text-4xl font-bold mb-4">Готовы начать?</h2>
            <p className="text-xl text-muted-foreground mb-8">
              Подключите свой банк и получите мгновенный доступ к AI-аналитике
            </p>
            <Link to="/dashboard">
              <Button variant="accent" size="lg" className="gap-2">
                Подключить банк через VTB Open API
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
