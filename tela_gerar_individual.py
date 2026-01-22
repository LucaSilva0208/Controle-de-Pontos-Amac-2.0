import tkinter as tk
from tkinter import messagebox
import json
from gerador_folha import GeradorFolhaPonto


class TelaGerarIndividual:
    def __init__(self, parent, voltar_callback):
        self.parent = parent
        self.voltar = voltar_callback

        self.frame = tk.Frame(parent, bg="#e5e7eb")
        self.frame.pack(fill="both", expand=True)

        self.criar_layout()
        self.carregar_funcionarios()

    def criar_layout(self):
        tk.Label(self.frame, text="Gerar Folha Individual",
                 font=("Segoe UI", 22, "bold"),
                 bg="#e5e7eb").pack(pady=20)

        self.func_var = tk.StringVar()
        self.mes_var = tk.StringVar()
        self.ano_var = tk.StringVar()

        tk.Label(self.frame, text="Funcionário").pack()
        self.combo = tk.OptionMenu(self.frame, self.func_var, "")
        self.combo.pack()

        tk.Label(self.frame, text="Mês").pack()
        tk.Entry(self.frame, textvariable=self.mes_var).pack()

        tk.Label(self.frame, text="Ano").pack()
        tk.Entry(self.frame, textvariable=self.ano_var).pack()

        tk.Button(self.frame, text="Gerar PDF", command=self.gerar).pack(pady=10)
        tk.Button(self.frame, text="⬅ Voltar", command=self.voltar).pack(pady=10)

    def carregar_funcionarios(self):
        with open("funcionarios.json", encoding="utf-8") as f:
            self.funcionarios = json.load(f)

        menu = self.combo["menu"]
        menu.delete(0, "end")
        for f in self.funcionarios:
            menu.add_command(label=f["nome"],
                             command=lambda v=f["nome"]: self.func_var.set(v))

    def gerar(self):
        nome = self.func_var.get()
        mes = self.mes_var.get()
        ano = self.ano_var.get()

        if not nome or not mes or not ano:
            messagebox.showwarning("Atenção", "Preencha todos os campos!")
            return

        func = next(f for f in self.funcionarios if f["nome"] == nome)
        gerador = GeradorFolhaPonto()
        gerador.gerar(func, mes, ano)

        messagebox.showinfo("OK", "Folha gerada com sucesso!")
