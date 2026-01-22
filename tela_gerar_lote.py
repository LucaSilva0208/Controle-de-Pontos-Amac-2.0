import tkinter as tk
from tkinter import messagebox
import json
from gerador_folha import GeradorFolhaPonto


class TelaGerarLote:
    def __init__(self, parent, voltar_callback):
        self.parent = parent
        self.voltar = voltar_callback

        self.frame = tk.Frame(parent, bg="#e5e7eb")
        self.frame.pack(fill="both", expand=True)

        self.criar_layout()
        self.carregar_funcionarios()

    def criar_layout(self):
        tk.Label(self.frame, text="Gerar Folhas em Lote",
                 font=("Segoe UI", 22, "bold"),
                 bg="#e5e7eb").pack(pady=20)

        self.busca = tk.StringVar()
        self.busca.trace_add("write", self.filtrar)

        tk.Entry(self.frame, textvariable=self.busca).pack(pady=10)

        self.frame_lista = tk.Frame(self.frame)
        self.frame_lista.pack(fill="both", expand=True)

        tk.Button(self.frame, text="Gerar Selecionados", command=self.gerar).pack(pady=10)
        tk.Button(self.frame, text="⬅ Voltar", command=self.voltar).pack(pady=10)

    def carregar_funcionarios(self):
        with open("funcionarios.json", encoding="utf-8") as f:
            self.funcionarios = json.load(f)
        self.atualizar_lista(self.funcionarios)

    def atualizar_lista(self, lista):
        for w in self.frame_lista.winfo_children():
            w.destroy()

        self.vars = []
        for f in lista:
            var = tk.BooleanVar(value=True)
            chk = tk.Checkbutton(
                self.frame_lista,
                text=f"{f['nome']} - {f['matricula']}",
                variable=var
            )
            chk.pack(anchor="w")
            self.vars.append((f, var))

    def filtrar(self, *args):
        termo = self.busca.get().lower()
        filtrados = [
            f for f in self.funcionarios
            if termo in f["nome"].lower() or termo in f["matricula"]
        ]
        self.atualizar_lista(filtrados)

    def gerar(self):
        selecionados = [f for f, v in self.vars if v.get()]

        if not selecionados:
            messagebox.showwarning("Atenção", "Nenhum funcionário selecionado.")
            return

        gerador = GeradorFolhaPonto()
        for f in selecionados:
            gerador.gerar(f, 1, 2026)

        messagebox.showinfo("OK", "Folhas geradas com sucesso!")
