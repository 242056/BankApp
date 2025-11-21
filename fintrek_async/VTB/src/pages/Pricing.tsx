import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Check, Sparkles, Crown, Zap } from "lucide-react";

const plans = [
  {
    name: "Free",
    price: "0",
    icon: Zap,
    description: "Для начала работы с финансами",
    features: [
      "1 банковский счёт",
      "Базовая аналитика",
      "Категоризация расходов",
      "Финансовый пульс",
      "Email поддержка",
    ],
    cta: "Начать бесплатно",
    variant: "outline" as const,
  },
  {
    name: "Premium",
    price: "499",
    icon: Sparkles,
    description: "Полный контроль над финансами",
    features: [
      "Неограниченное количество счетов",
      "Расширенная аналитика",
      "AI советы и рекомендации",
      "Планировщик сценариев",
      "Отслеживание инвестиций",
      "Экспорт отчётов",
      "Приоритетная поддержка",
    ],
    cta: "Выбрать Premium",
    variant: "accent" as const,
    popular: true,
  },
  {
    name: "Premium+",
    price: "999",
    icon: Crown,
    description: "Для профессионалов и инвесторов",
    features: [
      "Всё из Premium +",
      "ESG-анализ портфеля",
      "Автоматическая ребалансировка",
      "Персональный AI консультант",
      "Интеграция с брокерами",
      "API доступ",
      "Персональный менеджер",
    ],
    cta: "Выбрать Premium+",
    variant: "hero" as const,
  },
];

export default function Pricing() {
  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4">Выберите свой тариф</h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Начните бесплатно и обновите план когда будете готовы к расширенным возможностям
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {plans.map((plan, index) => (
            <Card
              key={index}
              className={`p-8 card-neo relative hover:shadow-xl transition-smooth ${
                plan.popular ? "ring-2 ring-accent scale-105" : ""
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="gradient-accent px-4 py-1 rounded-full text-xs font-semibold text-accent-foreground">
                    Популярный
                  </span>
                </div>
              )}

              <div className="text-center mb-6">
                <div className="gradient-accent w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <plan.icon className="w-8 h-8 text-accent-foreground" />
                </div>
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <p className="text-sm text-muted-foreground mb-4">{plan.description}</p>
                <div className="flex items-end justify-center gap-1">
                  <span className="text-5xl font-bold">₽{plan.price}</span>
                  <span className="text-muted-foreground mb-2">/месяц</span>
                </div>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <Button variant={plan.variant} className="w-full" size="lg">
                {plan.cta}
              </Button>
            </Card>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="mt-24 max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Часто задаваемые вопросы</h2>
          
          <div className="space-y-6">
            <Card className="p-6 card-neo">
              <h3 className="font-semibold mb-2">Можно ли отменить подписку?</h3>
              <p className="text-sm text-muted-foreground">
                Да, вы можете отменить подписку в любое время. Доступ к премиум-функциям сохранится до конца оплаченного периода.
              </p>
            </Card>

            <Card className="p-6 card-neo">
              <h3 className="font-semibold mb-2">Безопасны ли мои данные?</h3>
              <p className="text-sm text-muted-foreground">
                Мы используем банковский уровень шифрования и интегрируемся через VTB Open API. Мы не храним данные для входа в банк.
              </p>
            </Card>

            <Card className="p-6 card-neo">
              <h3 className="font-semibold mb-2">Какие банки поддерживаются?</h3>
              <p className="text-sm text-muted-foreground">
                Мы поддерживаем все крупные российские банки через VTB Open API. Полный список доступен в настройках подключения.
              </p>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
