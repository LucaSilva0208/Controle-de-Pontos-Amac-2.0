import tkinter as tk
from tela_gerar_individual import TelaGerarIndividual
from tela_gerar_lote import TelaGerarLote

class TelaPrincipal:
    def __init__(self, root, perfil):
        self.root = root
        self.perfil = perfil
        self.root.title("Ponto Certo - Sistema Corporativo de Folha de Ponto")
        self.root.state("zoomed")
        self.root.configure(bg="#0b1220")

        self.criar_layout()
        self.mostrar_home()

    def criar_layout(self):
        self.container = tk.Frame(self.root, bg="#0b1220")
        self.container.pack(fill="both", expand=True)

        # Sidebar
        self.menu = tk.Frame(self.container, bg="#020617", width=280)
        self.menu.pack(side="left", fill="y")
        self.menu.pack_propagate(False)

        tk.Label(
            self.menu,
            text="PONTO CERTO",
            fg="white", bg="#020617",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(30, 10))

        tk.Label(
            self.menu,
            text=f"Perfil: {self.perfil.upper()}",
            fg="#94a3b8", bg="#020617",
            font=("Segoe UI", 11)
        ).pack(pady=(0, 30))

        # Botões funcionais
        self.btn_individual = self.criar_botao("Gerar Folha Individual", self.abrir_individual)
        self.btn_lote = self.criar_botao("Gerar em Lote", self.abrir_lote)
        tk.Frame(self.menu, height=40, bg="#020617").pack()
        self.criar_botao("Sair do Sistema", self.sair)

        # Área dinâmica
        self.area = tk.Frame(self.container, bg="#0b1220")
        self.area.pack(side="right", fill="both", expand=True, padx=40, pady=40)

    def criar_botao(self, texto, comando):
        btn = tk.Button(
            self.menu,
            text=texto,
            command=lambda b=texto: self.executar(b, comando),
            bg="#020617",
            fg="#e5e7eb",
            activebackground="#1e293b",
            activeforeground="white",
            bd=0,
            anchor="w",
            padx=25,
            font=("Segoe UI", 12),
            height=2
        )
        btn.pack(fill="x", pady=6)
        return btn

    def executar(self, nome, comando):
        self.atualizar_selecao(nome)
        self.limpar_area()
        comando()

    def atualizar_selecao(self, nome):
        for widget in self.menu.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(bg="#020617")

        for widget in self.menu.winfo_children():
            if isinstance(widget, tk.Button) and nome in widget.cget("text"):
                widget.config(bg="#1e293b")

    def limpar_area(self):
        for w in self.area.winfo_children():
            w.destroy()

    def mostrar_home(self):
        self.limpar_area()
        card = tk.Frame(self.area, bg="#020617")
        card.pack(pady=100, ipadx=50, ipady=40)

        tk.Label(
            card,
            text="Bem-vindo ao Sistema Ponto Certo",
            font=("Segoe UI", 26, "bold"),
            bg="#020617", fg="white"
        ).pack(pady=(0, 10))

        tk.Label(
            card,
            text="Plataforma corporativa para geração automática\nde folhas de ponto em PDF.",
            font=("Segoe UI", 14),
            bg="#020617", fg="#cbd5e1",
            justify="center"
        ).pack()

    def abrir_individual(self):
        TelaGerarIndividual(self.area, self.mostrar_home)

    def abrir_lote(self):
        TelaGerarLote(self.area, self.mostrar_home)

    def sair(self):
        self.root.destroy()
