import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/contexts/AuthContext";
import { fetchMe, updateMe } from "@/api/users";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { User, Bell, CreditCard, Download, LogOut } from "lucide-react";
import { toast } from "sonner";
import { fetchBankConnections, createBankConnection, deleteBankConnection, syncBankConnection } from "@/api/bankConnections";
import { vbankSyncAccounts } from "@/api/vbank";
import { fetchAccounts, createAccount, updateAccount as updateAccountApi, deleteAccount as deleteAccountApi } from "@/api/accounts";

function BankConnectionsSection() {
  const qc = useQueryClient();
  const { data: list, isLoading } = useQuery({ queryKey: ["bank-connections"], queryFn: fetchBankConnections, onError: () => toast.error("Не удалось загрузить подключения") });

  const [bankName, setBankName] = useState("");
  const [bankBic, setBankBic] = useState("");

  const addMut = useMutation({
    mutationFn: () => createBankConnection({ bank_name: bankName, bank_bic: bankBic || undefined }),
    onSuccess: () => { toast.success("Банк добавлен"); setBankName(""); setBankBic(""); qc.invalidateQueries({ queryKey: ["bank-connections"] }); },
    onError: (e: any) => toast.error(e?.message || "Ошибка добавления"),
  });

  const delMut = useMutation({
    mutationFn: (id: string) => deleteBankConnection(id),
    onSuccess: () => { toast.success("Подключение отключено"); qc.invalidateQueries({ queryKey: ["bank-connections"] }); },
    onError: (e: any) => toast.error(e?.message || "Ошибка отключения"),
  });

  const syncMut = useMutation({
    mutationFn: (id: string) => syncBankConnection(id),
    onSuccess: () => toast.success("Синхронизация запущена"),
    onError: (e: any) => toast.error(e?.message || "Ошибка синхронизации"),
  });

  const vbankMut = useMutation({
    mutationFn: vbankSyncAccounts,
    onSuccess: () => { toast.success("Импорт счетов из VBank запущен"); },
    onError: (e: any) => toast.error(e?.message || "Ошибка импорта VBank"),
  });

  return (
    <div className="space-y-3">
      <div className="grid md:grid-cols-3 gap-3">
        <Input placeholder="Название банка" value={bankName} onChange={(e)=>setBankName(e.target.value)} />
        <Input placeholder="BIC (опционально)" value={bankBic} onChange={(e)=>setBankBic(e.target.value)} />
        <Button variant="outline" onClick={()=>addMut.mutate()} disabled={!bankName || addMut.isPending}>Добавить</Button>
      </div>

      <Button variant="outline" onClick={()=>vbankMut.mutate()} disabled={vbankMut.isPending}>
        + Импорт счетов через VBank
      </Button>

      {isLoading ? (
        <div className="text-sm text-muted-foreground">Загрузка подключений...</div>
      ) : (list?.connections?.length ? (
        list.connections.map(c => (
          <div key={c.id} className="flex items-center justify-between p-4 rounded-xl bg-secondary">
            <div>
              <p className="font-semibold">{c.bank_name}</p>
              <p className="text-sm text-muted-foreground">Статус: {c.status}{c.bank_bic ? ` • BIC ${c.bank_bic}` : ""}</p>
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={()=>syncMut.mutate(c.id)} disabled={syncMut.isPending}>Синхр.</Button>
              <Button size="sm" variant="outline" onClick={()=>delMut.mutate(c.id)} disabled={delMut.isPending}>Отключить</Button>
            </div>
          </div>
        ))
      ) : (
        <div className="text-sm text-muted-foreground">Подключений нет</div>
      ))}
    </div>
  );
}

function AccountsSection() {
  const qc = useQueryClient();
  const { data: list, isLoading } = useQuery({ queryKey: ["accounts"], queryFn: fetchAccounts });
  const [name, setName] = useState("");
  const [type, setType] = useState("checking");
  const [number, setNumber] = useState("");
  const [editId, setEditId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");

  const createMut = useMutation({
    mutationFn: () => createAccount({ account_name: name, account_type: type, account_number: number || undefined }),
    onSuccess: () => { toast.success("Счет создан"); setName(""); setNumber(""); qc.invalidateQueries({ queryKey: ["accounts"] }); },
    onError: (e: any) => toast.error(e?.message || "Ошибка создания счета"),
  });
  const saveMut = useMutation({
    mutationFn: () => (editId ? updateAccountApi(editId, { account_name: editName }) : Promise.resolve()),
    onSuccess: () => { toast.success("Счет обновлён"); setEditId(null); setEditName(""); qc.invalidateQueries({ queryKey: ["accounts"] }); },
    onError: (e: any) => toast.error(e?.message || "Ошибка обновления"),
  });
  const deleteMut = useMutation({
    mutationFn: (id: string) => deleteAccountApi(id),
    onSuccess: () => { toast.success("Счет удалён"); qc.invalidateQueries({ queryKey: ["accounts"] }); },
    onError: (e: any) => toast.error(e?.message || "Ошибка удаления"),
  });

  return (
    <div className="space-y-4">
      <div className="grid md:grid-cols-4 gap-3">
        <Input placeholder="Название" value={name} onChange={(e)=>setName(e.target.value)} />
        <select className="px-3 py-2 rounded-md border bg-background" value={type} onChange={(e)=>setType(e.target.value)}>
          <option value="checking">Расчетный</option>
          <option value="savings">Сберегательный</option>
          <option value="investment">Инвестиционный</option>
          <option value="credit">Кредитный</option>
        </select>
        <Input placeholder="Номер (опц.)" value={number} onChange={(e)=>setNumber(e.target.value)} />
        <Button variant="outline" onClick={()=>createMut.mutate()} disabled={!name || createMut.isPending}>Добавить</Button>
      </div>

      {isLoading ? (
        <div className="text-sm text-muted-foreground">Загрузка счетов...</div>
      ) : (
        <div className="space-y-2">
          {(list?.accounts || []).map(acc => (
            <div key={acc.id} className="flex items-center justify-between p-3 rounded-xl bg-secondary">
              <div className="flex items-center gap-3">
                {editId === String(acc.id) ? (
                  <Input value={editName} onChange={(e)=>setEditName(e.target.value)} className="w-[240px]" />
                ) : (
                  <span className="font-medium">{acc.account_name}</span>
                )}
                <span className="text-xs text-muted-foreground">{acc.account_type}</span>
                <span className="text-xs text-muted-foreground">₽{Number(acc.balance).toLocaleString()}</span>
              </div>
              <div className="flex gap-2">
                {editId === String(acc.id) ? (
                  <>
                    <Button size="sm" variant="outline" onClick={()=>saveMut.mutate()} disabled={saveMut.isPending || !editName}>Сохранить</Button>
                    <Button size="sm" variant="ghost" onClick={()=>{ setEditId(null); setEditName(""); }}>Отмена</Button>
                  </>
                ) : (
                  <>
                    <Button size="sm" variant="outline" onClick={()=>{ setEditId(String(acc.id)); setEditName(acc.account_name); }}>Переименовать</Button>
                    <Button size="sm" variant="destructive" onClick={()=>deleteMut.mutate(String(acc.id))} disabled={deleteMut.isPending}>Удалить</Button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Profile() {
  const { logout } = useAuth();
  const { data: me, isLoading: loadingMe } = useQuery({ queryKey: ["me"], queryFn: fetchMe, onError: () => toast.error("Не удалось загрузить профиль") });

  const [firstName, setFirstName] = useState("Александр");
  const [lastName, setLastName] = useState("Иванов");
  const [email, setEmail] = useState("alexandr@example.com");

  useEffect(() => {
    if (me) {
      setEmail(me.email);
      // В бэке одно поле name. Разобьём на 2 части визуально без изменения эндпоинтов.
      const parts = (me.name || "").split(" ");
      setFirstName(parts[0] || "");
      setLastName(parts.slice(1).join(" ") || "");
    }
  }, [me]);

  const saveMut = useMutation({
    mutationFn: async () => {
      const full_name = [firstName, lastName].filter(Boolean).join(" ");
      return updateMe({ full_name, email });
    },
    onSuccess: () => toast.success("Профиль обновлён"),
    onError: (e: any) => toast.error(e?.message || "Ошибка сохранения"),
  });

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
            <User className="w-10 h-10 text-accent" />
            Профиль
          </h1>
          <p className="text-muted-foreground">Управление аккаунтом и настройками</p>
        </div>

        {/* Profile Information */}
        <Card className="p-6 card-neo mb-6">
          <h3 className="text-xl font-semibold mb-6">Личная информация</h3>
          
          <div className="flex items-center gap-6 mb-6">
            <div className={`w-24 h-24 rounded-full gradient-accent flex items-center justify-center text-3xl font-bold text-accent-foreground ${loadingMe ? "animate-pulse" : ""}`}>
              {firstName?.[0]?.toUpperCase() || "А"}{lastName?.[0]?.toUpperCase() || "И"}
            </div>
            <div>
              <Button variant="outline" size="sm">Изменить фото</Button>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <Label htmlFor="firstName">Имя</Label>
              <Input id="firstName" value={firstName} onChange={(e)=>setFirstName(e.target.value)} className="mt-2" disabled={loadingMe || saveMut.isPending} />
            </div>
            <div>
              <Label htmlFor="lastName">Фамилия</Label>
              <Input id="lastName" value={lastName} onChange={(e)=>setLastName(e.target.value)} className="mt-2" disabled={loadingMe || saveMut.isPending} />
            </div>
            <div className="md:col-span-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" value={email} onChange={(e)=>setEmail(e.target.value)} className="mt-2" disabled={loadingMe || saveMut.isPending} />
            </div>
          </div>

          <Button onClick={()=>saveMut.mutate()} variant="accent" className="mt-6" disabled={saveMut.isPending}>Сохранить изменения</Button>
        </Card>

        {/* Notifications */}
        <Card className="p-6 card-neo mb-6">
          <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <Bell className="w-5 h-5 text-accent" />
            Уведомления
          </h3>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Email уведомления</p>
                <p className="text-sm text-muted-foreground">Получать отчёты и советы на email</p>
              </div>
              <Switch defaultChecked />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Push уведомления</p>
                <p className="text-sm text-muted-foreground">Важные события и превышения бюджета</p>
              </div>
              <Switch defaultChecked />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">AI рекомендации</p>
                <p className="text-sm text-muted-foreground">Умные советы по оптимизации финансов</p>
              </div>
              <Switch defaultChecked />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Недельные отчёты</p>
                <p className="text-sm text-muted-foreground">Сводка по расходам каждую неделю</p>
              </div>
              <Switch />
            </div>
          </div>
        </Card>

        {/* Connected Banks */}
        <Card className="p-6 card-neo mb-6">
          <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <CreditCard className="w-5 h-5 text-accent" />
            Подключённые банки
          </h3>

          <BankConnectionsSection />
        </Card>

        {/* Accounts */}
        <Card className="p-6 card-neo mb-6">
          <h3 className="text-xl font-semibold mb-6">Счета</h3>
          <AccountsSection />
        </Card>

        {/* Export & Settings */}
        <Card className="p-6 card-neo mb-6">
          <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <Download className="w-5 h-5 text-accent" />
            Экспорт данных
          </h3>

          <div className="space-y-3">
            <Button variant="outline" className="w-full justify-start gap-2">
              <Download className="w-4 h-4" />
              Скачать отчёт в PDF
            </Button>
            <Button variant="outline" className="w-full justify-start gap-2">
              <Download className="w-4 h-4" />
              Экспортировать в Excel
            </Button>
          </div>
        </Card>

        {/* Danger Zone */}
        <Card className="p-6 border-2 border-destructive/20 bg-destructive/5">
          <h3 className="text-xl font-semibold mb-4 text-destructive">Опасная зона</h3>
          <div className="space-y-3">
            <Button onClick={logout} variant="outline" className="w-full justify-start gap-2 text-destructive border-destructive/50 hover:bg-destructive/10">
              <LogOut className="w-4 h-4" />
              Выйти из аккаунта
            </Button>
            <Button variant="destructive" className="w-full">
              Удалить аккаунт
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
