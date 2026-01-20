import tkinter as tk
from tela_gerar_individual import TelaGerarIndividual
from tela_gerar_lote import TelaGerarLote


class TelaPrincipal:
    def __init__(self, root, perfil):
        self.root = root
        self.root.title("Ponto Certo - Sistema de Folha de Ponto")
        self.root.state("zoomed")

        self.perfil = perfil
        self.btns_menu = []
        self.criar_layout()

    def criar_layout(self):
        self.container = tk.Frame(self.root, bg="#f3f4f6")
        self.container.pack(fill="both", expand=True)

        topo = tk.Frame(self.container, bg="#0f172a", height=60)
        topo.pack(fill="x")
        topo.pack_propagate(False)

        tk.Label(topo, text="Ponto Certo — Sistema de Folha de Ponto",
                 fg="white", bg="#0f172a",
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=20)

        tk.Label(topo, text=f"Perfil: {self.perfil.upper()}",
                 fg="#cbd5e1", bg="#0f172a",
                 font=("Segoe UI", 10)).pack(side="right", padx=20)

        corpo = tk.Frame(self.container, bg="#e5e7eb")
        corpo.pack(fill="both", expand=True)

        self.menu = tk.Frame(corpo, bg="#020617", width=240)
        self.menu.pack(side="left", fill="y")
        self.menu.pack_propagate(False)

        tk.Label(self.menu, text="MENU",
                 fg="#94a3b8", bg="#020617",
                 font=("Segoe UI", 10, "bold")).pack(pady=(20, 10), anchor="w", padx=20)

        self.add_btn("📄  Gerar Folha Individual", lambda: self.abrir(TelaGerarIndividual))
        self.add_btn("📦  Gerar em Lote", lambda: self.abrir(TelaGerarLote))
        self.add_btn("🚪  Sair do Sistema", self.sair)

        self.area = tk.Frame(corpo, bg="white")
        self.area.pack(side="right", fill="both", expand=True)

        tk.Label(self.area, text="Bem-vindo ao Ponto Certo",
                 font=("Segoe UI", 24, "bold"), bg="white").pack(pady=(60, 10))

        tk.Label(self.area,
                 text="Escolha uma opção no menu lateral para continuar.",
                 font=("Segoe UI", 13), bg="white").pack()

    def add_btn(self, texto, comando):
        btn = tk.Button(
            self.menu, text=texto, command=lambda b=texto: self.select(b, comando),
            bg="#020617", fg="#e5e7eb",
            activebackground="#1e293b",
            activeforeground="white",
            bd=0, anchor="w",
            padx=25, pady=10,
            font=("Segoe UI", 11)
        )
        btn.pack(fill="x")
        self.btns_menu.append(btn)

        btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#1e293b"))
        btn.bind("<Leave>", lambda e, b=btn: self.reset_hover(b))

    def select(self, texto, comando):
        for b in self.btns_menu:
            b.configure(bg="#020617")
        widget = self.root.focus_get()
        widget.configure(bg="#334155")  # botão ativo
        comando()

    def reset_hover(self, btn):
        if btn.cget("bg") != "#334155":
            btn.configure(bg="#020617")

    def abrir(self, tela):
        tela(self.root)

    def sair(self):
        self.root.destroy()
