import tkinter as tk
from tkinter import messagebox
import json
from gerador_pdf import GeradorFolhaPDF

ARQ_FUNC = "funcionarios.json"


class TelaGerarLote:
    def __init__(self, master):
        self.win = tk.Toplevel(master)
        self.win.title("Gerar Folhas em Lote")
        self.win.state("zoomed")

        self.criar_layout()
        self.carregar_funcionarios()

    def criar_layout(self):
        container = tk.Frame(self.win, bg="#f1f3f5")
        container.pack(fill="both", expand=True)

        # 🔹 Topo
        topo = tk.Frame(container, bg="#111827", height=60)
        topo.pack(fill="x")
        topo.pack_propagate(False)

        tk.Button(
            topo, text="⬅ Voltar ao Menu",
            command=self.win.destroy,
            bg="#111827", fg="white",
            bd=0, font=("Segoe UI", 12, "bold"),
            padx=15
        ).pack(side="left", pady=10)

        tk.Label(
            topo, text="Gerar Folhas em Lote",
            fg="white", bg="#111827",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left", padx=20)

        # 🔹 Conteúdo
        conteudo = tk.Frame(container, bg="#e5e7eb")
        conteudo.pack(fill="both", expand=True, padx=40, pady=30)

        frame_top = tk.Frame(conteudo, bg="#e5e7eb")
        frame_top.pack(fill="x")

        tk.Label(
            frame_top,
            text="Buscar por nome ou matrícula:",
            bg="#e5e7eb"
        ).pack(anchor="w")

        self.var_busca = tk.StringVar()
        self.var_busca.trace_add("write", self.filtrar)

        tk.Entry(
            frame_top,
            textvariable=self.var_busca,
            width=45
        ).pack(anchor="w", pady=5)

        self.lbl_contador = tk.Label(
            frame_top,
            text="Selecionados: 0",
            bg="#e5e7eb",
            fg="#374151",
            font=("Segoe UI", 10, "bold")
        )
        self.lbl_contador.pack(anchor="e")

        # 🔹 Lista
        frame_lista = tk.Frame(conteudo, bg="white")
        frame_lista.pack(fill="both", expand=True, pady=10)

        canvas = tk.Canvas(frame_lista, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_lista, orient="vertical", command=canvas.yview)

        self.frame_itens = tk.Frame(canvas, bg="white")

        self.frame_itens.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.frame_itens, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 🔹 Botões
        frame_botoes = tk.Frame(conteudo, bg="#e5e7eb")
        frame_botoes.pack(fill="x", pady=10)

        tk.Button(
            frame_botoes, text="Cancelar Seleção",
            font=("Segoe UI", 12, "bold"),
            bg="#ef4444", fg="white",
            command=self.cancelar_selecao
        ).pack(side="left", padx=5)

        tk.Button(
            frame_botoes, text="Gerar Folhas",
            font=("Segoe UI", 12, "bold"),
            bg="#16a34a", fg="white",
            command=self.gerar
        ).pack(side="right", padx=5)

    def cor_status(self, status):
        status = status.lower()
        if status == "ativo":
            return "#16a34a"
        if status == "férias":
            return "#d97706"
        return "#dc2626"

    def carregar_funcionarios(self):
        try:
            with open(ARQ_FUNC, "r", encoding="utf-8") as f:
                self.funcionarios = json.load(f)
        except:
            self.funcionarios = []

        self.funcionarios.sort(key=lambda x: x["nome"].lower())
        self.vars = []
        self.atualizar_lista(self.funcionarios)

    def atualizar_lista(self, lista):
        for w in self.frame_itens.winfo_children():
            w.destroy()

        self.vars.clear()

        for f in lista:
            var = tk.BooleanVar(value=True)
            var.trace_add("write", self.atualizar_contador)

            chk = tk.Checkbutton(
                self.frame_itens,
                text=f"{f['nome']} — {f['cargo']} ({f['status']})",
                variable=var,
                fg=self.cor_status(f["status"]),
                bg="white",
                anchor="w"
            )
            chk.pack(fill="x", padx=10, pady=2)

            self.vars.append((f, var))

        self.atualizar_contador()

    def atualizar_contador(self, *args):
        total = sum(1 for _, v in self.vars if v.get())
        self.lbl_contador.config(text=f"Selecionados: {total}")

    def filtrar(self, *args):
        termo = self.var_busca.get().lower()
        filtrados = [
            f for f in self.funcionarios
            if termo in f["nome"].lower() or termo in f["matricula"].lower()
        ]
        self.atualizar_lista(filtrados)

    def cancelar_selecao(self):
        for _, v in self.vars:
            v.set(False)

    def gerar(self):
        selecionados = [f for f, v in self.vars if v.get()]
        if not selecionados:
            messagebox.showwarning("Atenção", "Nenhum funcionário selecionado.")
            return

        for f in selecionados:
            nome_arq = f"Folha_{f['nome'].replace(' ', '_')}.pdf"
            gerador = GeradorFolhaPDF(nome_arq)
            gerador.gerar_folha(
                f["nome"],
                f["cargo"],
                f["matricula"],
                "MÊS ATUAL",
                f.get("status", "ativo")
            )

        messagebox.showinfo("OK", f"{len(selecionados)} folhas geradas com sucesso!")
        self.win.destroy()
