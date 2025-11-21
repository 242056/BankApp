import { useMemo, useState, useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowUpRight, ArrowDownLeft, Download, Filter, Repeat, Search, Send } from "lucide-react";
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { fetchAccounts } from "@/api/accounts";
import { fetchTransactions, createTransaction, updateTransaction } from "@/api/transactions";
import { fetchCategories, createCategory, updateCategory as updateCategoryApi, deleteCategory as deleteCategoryApi } from "@/api/categories";
import { vbankSyncTransactions } from "@/api/vbank";
import { toast } from "sonner";

// Mock fallbacks (analytics tab + templates kept as-is)
const accountOptionsMock: any[] = [];

const recentTransactionsMock: any[] = [];

const savedTemplates: Array<{ id: number; name: string; recipient: string; amount: number }> = [];

// TODO: Replace with real analytics data from API
const transferAnalytics: any[] = [];

const monthlyActivity: any[] = [];

const COLORS = ["hsl(175 100% 39%)", "hsl(215 76% 16%)", "hsl(175 80% 50%)", "hsl(215 60% 25%)"];

function CategoriesManager() {
  const qc = useQueryClient();
  const { data: catList } = useQuery({ queryKey: ["categories"], queryFn: fetchCategories });
  const [name, setName] = useState("");
  const [type, setType] = useState("expense");
  const [editId, setEditId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");

  const createMut = useMutation({
    mutationFn: () => createCategory({ name, category_type: type }),
    onSuccess: () => { toast.success("Категория создана"); setName(""); qc.invalidateQueries({ queryKey: ["categories"] }); },
    onError: (e: any) => toast.error(e?.message || "Ошибка создания категории"),
  });
  const saveMut = useMutation({
    mutationFn: () => (editId ? updateCategoryApi(editId, { name: editName }) : Promise.resolve()),
    onSuccess: () => { toast.success("Категория сохранена"); setEditId(null); setEditName(""); qc.invalidateQueries({ queryKey: ["categories"] }); },
    onError: (e: any) => toast.error(e?.message || "Ошибка сохранения"),
  });
  const deleteMut = useMutation({
    mutationFn: (id: string) => deleteCategoryApi(id),
    onSuccess: () => { toast.success("Категория удалена"); qc.invalidateQueries({ queryKey: ["categories"] }); },
    onError: (e: any) => toast.error(e?.message || "Ошибка удаления"),
  });

  return (
    <div className="space-y-4">
      <div className="grid md:grid-cols-3 gap-3">
        <Input placeholder="Название категории" value={name} onChange={(e) => setName(e.target.value)} />
        <Select value={type} onValueChange={setType}>
          <SelectTrigger><SelectValue placeholder="Тип" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="expense">Расход</SelectItem>
            <SelectItem value="income">Доход</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="outline" onClick={() => createMut.mutate()} disabled={!name || createMut.isPending}>Добавить</Button>
      </div>

      <div className="space-y-2">
        {(catList?.categories || []).map(c => (
          <div key={c.id} className="flex items-center justify-between p-3 rounded-xl bg-secondary">
            <div className="flex items-center gap-2">
              {editId === c.id ? (
                <Input value={editName} onChange={(e) => setEditName(e.target.value)} className="w-[240px]" />
              ) : (
                <span className="font-medium">{c.name}</span>
              )}
              <span className="text-xs text-muted-foreground">{c.category_type}</span>
            </div>
            <div className="flex gap-2">
              {editId === c.id ? (
                <>
                  <Button size="sm" variant="outline" onClick={() => saveMut.mutate()} disabled={saveMut.isPending || !editName}>Сохранить</Button>
                  <Button size="sm" variant="ghost" onClick={() => { setEditId(null); setEditName(""); }}>Отмена</Button>
                </>
              ) : (
                <>
                  <Button size="sm" variant="outline" onClick={() => { setEditId(c.id); setEditName(c.name); }}>Переименовать</Button>
                  <Button size="sm" variant="destructive" onClick={() => deleteMut.mutate(c.id)} disabled={deleteMut.isPending}>Удалить</Button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Transfers() {
  const qc = useQueryClient();
  const [selectedAccount, setSelectedAccount] = useState("");
  const [recipient, setRecipient] = useState("");
  const [amount, setAmount] = useState("");
  const [comment, setComment] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [filterCategory, setFilterCategory] = useState("all");
  const [filterBank, setFilterBank] = useState("all");
  const [editTxId, setEditTxId] = useState<string | null>(null);

  // VBank import controls
  const [extAccountId, setExtAccountId] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  // History filters
  const [histAccountId, setHistAccountId] = useState<string>("");
  const [histFrom, setHistFrom] = useState<string>("");
  const [histTo, setHistTo] = useState<string>("");

  const { data: accounts, isLoading: loadingAccounts, isError: isAccountsError, error: accountsError } = useQuery({
    queryKey: ["accounts"],
    queryFn: fetchAccounts
  });

  useEffect(() => {
    if (isAccountsError) toast.error("Не удалось загрузить счета");
  }, [isAccountsError]);

  const accountOptions = useMemo(() => {
    const accs = (accounts as any)?.accounts || [];
    if (!accs.length) return [] as Array<{ id: string; name: string; balance: number; bank: string }>;
    return accs.map((a: any) => ({
      id: a.id,
      name: a.account_name,
      balance: Number(a.balance ?? 0),
      bank: "—",
    }));
  }, [accounts]);

  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const { data: txList, isLoading: loadingTx, isError: isTxError } = useQuery({
    queryKey: ["transactions", page, filterCategory, histAccountId, histFrom, histTo, pageSize],
    queryFn: () => fetchTransactions({
      page,
      page_size: pageSize,
      category_id: filterCategory !== "all" ? filterCategory : undefined,
      account_id: histAccountId || undefined,
      date_from: histFrom || undefined,
      date_to: histTo || undefined,
    }),
  });

  useEffect(() => {
    if (isTxError) toast.error("Не удалось загрузить операции");
  }, [isTxError]);

  const { data: catList } = useQuery({ queryKey: ["categories"], queryFn: fetchCategories });
  const catMap = useMemo(() => {
    const m = new Map<string, string>();
    const cats = (catList as any)?.categories || [];
    cats.forEach((c: any) => m.set(c.id, c.name));
    return m;
  }, [catList]);
  const recentTransactions = useMemo(() => {
    const txs = (txList as any)?.transactions || [];
    if (!txs.length) return [] as Array<any>;
    return txs.map((t: any) => {
      const categoryId = (t as any).category_id ?? (t as any).categoryId;
      const categoryName = catMap.get(String(categoryId)) || (t as any).category || "—";
      // Ensure ID is a string and fallback to randomUUID if missing (though it shouldn't be)
      const txId = (t as any).id ? String((t as any).id) : crypto.randomUUID();

      return {
        id: txId,
        date: String((t as any).transaction_date ?? (t as any).date ?? "").slice(0, 10),
        type: ((t as any).transaction_type ?? (t as any).type ?? "expense").toLowerCase() === "income" ? "incoming" : "outgoing",
        recipient: (t as any).merchant_name ?? (t as any).recipient ?? "",
        amount: Number((t as any).amount ?? 0),
        category: categoryName,
        category_id: categoryId ? String(categoryId) : undefined,
        status: ((t as any).status ?? "completed").toLowerCase(),
        description: (t as any).description ?? "",
        bank: "—",
      };
    });
  }, [txList, catMap]);

  const createMut = useMutation({
    mutationFn: async () => {
      if (!selectedAccount || !recipient || !amount) throw new Error("Заполните счет, получателя и сумму");
      const amt = Number(amount);
      if (!Number.isFinite(amt) || amt <= 0) throw new Error("Сумма должна быть положительным числом");
      return createTransaction({
        account_id: selectedAccount,
        transaction_type: "expense",
        amount: amt,
        merchant_name: recipient,
        description: comment || undefined,
        transaction_date: new Date().toISOString(),
      });
    },
    onSuccess: () => {
      toast.success("Перевод успешно отправлен");
      qc.invalidateQueries({ queryKey: ["transactions"] });
      setRecipient(""); setAmount(""); setComment("");
    },
    onError: (e: any) => {
      toast.error(e?.message || "Ошибка при отправке перевода");
    }
  });

  const updateCategoryMut = useMutation({
    mutationFn: async ({ id, category_id }: { id: string; category_id: string }) => updateTransaction(id, { category_id }),
    onSuccess: () => { toast.success("Категория обновлена"); qc.invalidateQueries({ queryKey: ["transactions"] }); setEditTxId(null); },
    onError: (e: any) => toast.error(e?.message || "Ошибка обновления категории"),
  });

  const updateStatusMut = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: string }) => updateTransaction(id, { status }),
    onSuccess: () => { toast.success("Статус обновлён"); qc.invalidateQueries({ queryKey: ["transactions"] }); setEditTxId(null); },
    onError: (e: any) => toast.error(e?.message || "Ошибка обновления статуса"),
  });

  const updateNotesMut = useMutation({
    mutationFn: async ({ id, description }: { id: string; description: string }) => updateTransaction(id, { description }),
    onSuccess: () => { toast.success("Комментарий обновлён"); qc.invalidateQueries({ queryKey: ["transactions"] }); setEditTxId(null); },
    onError: (e: any) => toast.error(e?.message || "Ошибка обновления комментария"),
  });

  const handleTransfer = (e: React.FormEvent) => {
    e.preventDefault();
    createMut.mutate();
  };

  const vbankSyncMut = useMutation({
    mutationFn: async () => {
      if (!extAccountId) throw new Error("Укажите внешний account_id");
      return vbankSyncTransactions(extAccountId, dateFrom || undefined, dateTo || undefined);
    },
    onSuccess: () => { toast.success("Импорт транзакций запущен"); qc.invalidateQueries({ queryKey: ["transactions"] }); },
    onError: (e: any) => toast.error(e?.message || "Ошибка импорта транзакций"),
  });

  const filteredTransactions = recentTransactions.filter((tx) => {
    const matchesSearch =
      tx.recipient.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tx.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (tx.description || "").toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = filterCategory === "all" || tx.category_id === filterCategory;
    const matchesBank = filterBank === "all" || tx.bank === filterBank;
    return matchesSearch && matchesCategory && matchesBank;
  });

  return (
    <div className="min-h-screen bg-background py-4 md:py-8">
      <div className="container mx-auto px-4">
        <div className="mb-6 md:mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">Переводы</h1>
          <p className="text-muted-foreground">Управляйте переводами и отслеживайте историю операций</p>
        </div>

        <Tabs defaultValue="transfer" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
            <TabsTrigger value="transfer">Перевод</TabsTrigger>
            <TabsTrigger value="history">История</TabsTrigger>
            <TabsTrigger value="analytics">Аналитика</TabsTrigger>
          </TabsList>

          {/* Transfer Tab */}
          <TabsContent value="transfer" className="space-y-6">
            <div className="grid lg:grid-cols-3 gap-6">
              {/* Transfer Form */}
              <Card className="p-4 md:p-6 card-neo lg:col-span-2">
                <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Send className="w-5 h-5 text-accent" />
                  Новый перевод
                </h3>
                <form onSubmit={handleTransfer} className="space-y-4">
                  <div>
                    <Label htmlFor="account">Счет списания</Label>
                    <Select value={selectedAccount} onValueChange={setSelectedAccount}>
                      <SelectTrigger id="account">
                        <SelectValue placeholder="Выберите счет" />
                      </SelectTrigger>
                      <SelectContent>
                        {loadingAccounts && accountOptions.length === 0 ? (
                          <div className="px-3 py-2 text-sm text-muted-foreground">Загрузка счетов...</div>
                        ) : accountOptions.length === 0 ? (
                          <div className="px-3 py-2 text-sm text-muted-foreground">Нет доступных счетов</div>
                        ) : (
                          accountOptions.map((acc) => (
                            <SelectItem key={acc.id} value={String(acc.id)}>
                              {acc.name} • {acc.bank} • ₽{acc.balance.toLocaleString()}
                            </SelectItem>
                          ))
                        )}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="recipient">Получатель</Label>
                    <Input
                      id="recipient"
                      placeholder="Номер карты, телефона или счета"
                      value={recipient}
                      onChange={(e) => setRecipient(e.target.value)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="amount">Сумма</Label>
                    <Input
                      id="amount"
                      type="number"
                      placeholder="0.00"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="comment">Комментарий (необязательно)</Label>
                    <Input
                      id="comment"
                      placeholder="Назначение платежа"
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                    />
                  </div>

                  <Button type="submit" className="w-full" variant="accent" disabled={createMut.isPending}>
                    <Send className="w-4 h-4 mr-2" />
                    {createMut.isPending ? "Отправка..." : "Отправить перевод"}
                  </Button>
                </form>
              </Card>

              {/* Saved Templates */}
              <Card className="p-4 md:p-6 card-neo">
                <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Repeat className="w-5 h-5 text-accent" />
                  Шаблоны
                </h3>
                <div className="space-y-3">
                  {savedTemplates.length === 0 ? (
                    <div className="text-sm text-muted-foreground">Нет шаблонов</div>
                  ) : savedTemplates.map((template) => (
                    <div
                      key={template.id}
                      className="p-3 rounded-lg border border-border hover:bg-secondary/50 transition-smooth cursor-pointer"
                      onClick={() => {
                        setRecipient(template.recipient);
                        setAmount(template.amount.toString());
                      }}
                    >
                      <div className="font-medium text-sm">{template.name}</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {template.recipient} • ₽{template.amount.toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            {/* VBank Import */}
            <Card className="p-4 md:p-6 card-neo">
              <h3 className="text-xl font-semibold mb-4">Импорт операций (VBank)</h3>
              <div className="grid md:grid-cols-4 gap-3">
                <Input placeholder="external account_id" value={extAccountId} onChange={(e) => setExtAccountId(e.target.value)} />
                <Input type="date" placeholder="date_from" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
                <Input type="date" placeholder="date_to" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
                <Button variant="outline" onClick={() => vbankSyncMut.mutate()} disabled={vbankSyncMut.isPending}>Синхронизировать</Button>
              </div>
            </Card>

            {/* Recent Activity */}
            <Card className="p-4 md:p-6 card-neo">
              <h3 className="text-xl font-semibold mb-4">Последние операции</h3>
              <div className="space-y-3">
                {loadingTx ? (
                  <div className="text-sm text-muted-foreground">Загрузка...</div>
                ) : recentTransactions.length === 0 ? (
                  <div className="text-sm text-muted-foreground">Нет операций</div>
                ) : (
                  recentTransactions.slice(0, 5).map((tx) => (
                    <div key={tx.id} className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-secondary/50 transition-smooth">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${tx.type === "incoming" ? "bg-accent/10" : "bg-muted"
                          }`}>
                          {tx.type === "incoming" ? (
                            <ArrowDownLeft className="w-5 h-5 text-accent" />
                          ) : (
                            <ArrowUpRight className="w-5 h-5 text-muted-foreground" />
                          )}
                        </div>
                        <div>
                          <div className="font-medium">{tx.recipient}</div>
                          <div className="text-xs text-muted-foreground">{tx.category} • {tx.date}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`font-semibold ${tx.type === "incoming" ? "text-accent" : ""}`}>
                          {tx.type === "incoming" ? "+" : "-"}₽{tx.amount.toLocaleString()}
                        </div>
                        <Badge variant={tx.status === "completed" ? "default" : "secondary"} className="text-xs">
                          {tx.status === "completed" ? "Выполнен" : "В ожидании"}
                        </Badge>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history" className="space-y-6">
            {/* Filters */}
            <Card className="p-4 md:p-6 card-neo">
              <div className="flex flex-col gap-4">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <Label htmlFor="search" className="sr-only">Поиск</Label>
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        id="search"
                        placeholder="Поиск по операциям..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Select value={filterCategory} onValueChange={setFilterCategory}>
                      <SelectTrigger className="w-full md:w-[180px]">
                        <Filter className="w-4 h-4 mr-2" />
                        <SelectValue placeholder="Категория" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Все категории</SelectItem>
                        {(catList?.categories || []).map(c => (
                          <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Select value={filterBank} onValueChange={setFilterBank}>
                      <SelectTrigger className="w-full md:w-[180px]">
                        <SelectValue placeholder="Банк" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Все банки</SelectItem>
                        <SelectItem value="ВТБ">ВТБ</SelectItem>
                        <SelectItem value="Сбербанк">Сбербанк</SelectItem>
                        <SelectItem value="Тинькофф">Тинькофф</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button variant="outline" size="icon">
                      <Download className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                <div className="grid md:grid-cols-3 gap-3">
                  <Select value={histAccountId} onValueChange={setHistAccountId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Счёт (фильтр)" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Все счета</SelectItem>
                      {accountOptions.map(acc => (
                        <SelectItem key={acc.id} value={String(acc.id)}>{acc.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Input type="date" value={histFrom} onChange={(e) => setHistFrom(e.target.value)} placeholder="Дата от" />
                  <Input type="date" value={histTo} onChange={(e) => setHistTo(e.target.value)} placeholder="Дата до" />
                </div>
              </div>
            </Card>

            {/* Categories Management */}
            <Card className="p-4 md:p-6 card-neo">
              <h3 className="text-xl font-semibold mb-4">Категории</h3>
              <CategoriesManager />
            </Card>

            {/* Transactions Table */}
            <Card className="p-4 md:p-6 card-neo overflow-hidden">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Дата</TableHead>
                      <TableHead>Тип</TableHead>
                      <TableHead>Получатель / Отправитель</TableHead>
                      <TableHead>Категория</TableHead>
                      <TableHead>Банк</TableHead>
                      <TableHead className="text-right">Сумма</TableHead>
                      <TableHead>Комментарий</TableHead>
                      <TableHead>Статус</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredTransactions.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={8} className="text-center text-sm text-muted-foreground">Нет операций</TableCell>
                      </TableRow>
                    ) : (
                      filteredTransactions.map((tx) => (
                        <TableRow key={tx.id}>
                          <TableCell className="whitespace-nowrap">{tx.date}</TableCell>
                          <TableCell>
                            {tx.type === "incoming" ? (
                              <ArrowDownLeft className="w-4 h-4 text-accent" />
                            ) : (
                              <ArrowUpRight className="w-4 h-4 text-muted-foreground" />
                            )}
                          </TableCell>
                          <TableCell className="font-medium">{tx.recipient}</TableCell>
                          <TableCell>
                            {editTxId === String(tx.id) ? (
                              <Select onValueChange={(val) => updateCategoryMut.mutate({ id: String(tx.id), category_id: val })}>
                                <SelectTrigger className="w-[180px]">
                                  <SelectValue placeholder="Выбрать категорию" />
                                </SelectTrigger>
                                <SelectContent>
                                  {(catList?.categories || []).map(c => (
                                    <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            ) : (
                              <Badge variant="outline" className="cursor-pointer" onClick={() => setEditTxId(String(tx.id))}>{tx.category}</Badge>
                            )}
                          </TableCell>
                          <TableCell className="text-muted-foreground">{tx.bank}</TableCell>
                          <TableCell className={`text-right font-semibold whitespace-nowrap ${tx.type === "incoming" ? "text-accent" : ""
                            }`}>
                            {tx.type === "incoming" ? "+" : "-"}₽{tx.amount.toLocaleString()}
                          </TableCell>
                          <TableCell className="w-[240px]">
                            {editTxId === String(tx.id) ? (
                              <div className="flex items-center gap-2">
                                <Input value={tx.description} onChange={(e) => { tx.description = e.target.value; }} placeholder="Комментарий" />
                                <Button size="sm" variant="outline" onClick={() => updateNotesMut.mutate({ id: String(tx.id), description: tx.description || "" })}>Сохранить</Button>
                                <Button size="sm" variant="ghost" onClick={() => setEditTxId(null)}>Отмена</Button>
                              </div>
                            ) : (
                              <span className="text-sm text-muted-foreground" onClick={() => setEditTxId(String(tx.id))}>{tx.description || "—"}</span>
                            )}
                          </TableCell>
                          <TableCell>
                            {editTxId === String(tx.id) ? (
                              <Select onValueChange={(val) => updateStatusMut.mutate({ id: String(tx.id), status: val })}>
                                <SelectTrigger className="w-[160px]">
                                  <SelectValue placeholder="Статус" />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="completed">Выполнен</SelectItem>
                                  <SelectItem value="pending">В ожидании</SelectItem>
                                  <SelectItem value="cancelled">Отменён</SelectItem>
                                </SelectContent>
                              </Select>
                            ) : (
                              <Badge variant={tx.status === "completed" ? "default" : "secondary"} className="cursor-pointer" onClick={() => setEditTxId(String(tx.id))}>
                                {tx.status === "completed" ? "Выполнен" : tx.status === "pending" ? "В ожидании" : "Отменён"}
                              </Badge>
                            )}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
                <div className="flex items-center justify-between mt-4">
                  <div className="text-sm text-muted-foreground">Стр. {page}</div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1}>Назад</Button>
                    <Button variant="outline" size="sm" onClick={() => setPage(p => p + 1)} disabled={(txList?.transactions?.length ?? 0) < pageSize}>Вперёд</Button>
                  </div>
                </div>
              </div>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Transfer Structure */}
              <Card className="p-4 md:p-6 card-neo">
                <h3 className="text-xl font-semibold mb-4">Структура переводов</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={transferAnalytics}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ₽${value.toLocaleString()}`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {transferAnalytics.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
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
              </Card>

              {/* Monthly Activity */}
              <Card className="p-4 md:p-6 card-neo">
                <h3 className="text-xl font-semibold mb-4">Активность по месяцам</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={monthlyActivity}>
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
                    <Bar dataKey="incoming" fill="hsl(175 100% 39%)" name="Входящие" radius={[8, 8, 0, 0]} />
                    <Bar dataKey="outgoing" fill="hsl(215 76% 16%)" name="Исходящие" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Stats Summary */}
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {transferAnalytics.map((item, index) => (
                <Card key={index} className="p-4 md:p-6 card-neo">
                  <div className="text-sm text-muted-foreground mb-2">{item.name}</div>
                  <div className="text-2xl font-bold mb-1" style={{ color: COLORS[index] }}>
                    ₽{item.value.toLocaleString()}
                  </div>
                  <div className="text-xs text-muted-foreground">{item.count} операций</div>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
