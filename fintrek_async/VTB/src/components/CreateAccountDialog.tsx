import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { createAccount } from "@/api/accounts";
import { toast } from "sonner";
import { Plus } from "lucide-react";

export function CreateAccountDialog() {
    const [open, setOpen] = useState(false);
    const [name, setName] = useState("");
    const [type, setType] = useState("checking");
    const [balance, setBalance] = useState("");
    const [currency, setCurrency] = useState("RUB");
    const qc = useQueryClient();

    const createMut = useMutation({
        mutationFn: () => createAccount({
            account_name: name,
            account_type: type,
            balance: Number(balance) || 0,
            currency
        }),
        onSuccess: () => {
            toast.success("Счет успешно создан");
            qc.invalidateQueries({ queryKey: ["account-summary"] });
            qc.invalidateQueries({ queryKey: ["accounts"] });
            setOpen(false);
            setName("");
            setBalance("");
            setType("checking");
        },
        onError: (e: any) => {
            toast.error(e?.message || "Ошибка создания счета");
        }
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!name) {
            toast.error("Введите название счета");
            return;
        }
        createMut.mutate();
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button className="gap-2">
                    <Plus className="w-4 h-4" />
                    Добавить счет
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Новый счет</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 mt-4">
                    <div className="space-y-2">
                        <Label htmlFor="name">Название</Label>
                        <Input
                            id="name"
                            placeholder="Например: Основной"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="type">Тип счета</Label>
                        <Select value={type} onValueChange={setType}>
                            <SelectTrigger>
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="checking">Текущий</SelectItem>
                                <SelectItem value="savings">Сберегательный</SelectItem>
                                <SelectItem value="credit">Кредитный</SelectItem>
                                <SelectItem value="investment">Инвестиционный</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="balance">Баланс</Label>
                            <Input
                                id="balance"
                                type="number"
                                placeholder="0"
                                value={balance}
                                onChange={(e) => setBalance(e.target.value)}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="currency">Валюта</Label>
                            <Select value={currency} onValueChange={setCurrency}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="RUB">RUB</SelectItem>
                                    <SelectItem value="USD">USD</SelectItem>
                                    <SelectItem value="EUR">EUR</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <div className="pt-4 flex justify-end gap-2">
                        <Button type="button" variant="ghost" onClick={() => setOpen(false)}>Отмена</Button>
                        <Button type="submit" disabled={createMut.isPending}>
                            {createMut.isPending ? "Создание..." : "Создать"}
                        </Button>
                    </div>
                </form>
            </DialogContent>
        </Dialog>
    );
}
