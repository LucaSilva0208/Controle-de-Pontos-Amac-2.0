import tkinter as tk
from tkinter import messagebox
from tela_gerar_individual import TelaGerarIndividual
from tela_gerar_lote import TelaGerarLote
# IMPORTAÇÃO CORRETA CONFORME SEU PEDIDO
from repositorio_usuarios import RepositorioUsuarios 

class TelaPrincipal:
    def __init__(self, root, dados_usuario):
        self.root = root
        self.dados_usuario = dados_usuario
        
        # Garante que pegamos o perfil corretamente
        if isinstance(dados_usuario, dict):
            self.perfil = dados_usuario.get('perfil', 'comum')
            self.usuario_nome = dados_usuario.get('usuario', 'Usuario')
        else:
            self.perfil = str(dados_usuario)
            self.usuario_nome = "Usuario"

        self.root.title(f"Ponto Certo - Usuário: {self.usuario_nome}")
        self.root.state("zoomed")
        self.root.configure(bg="#0b1220")
        self.root.resizable(True, True)

        self.criar_layout()
        self.mostrar_home()

    def criar_layout(self):
        self.container = tk.Frame(self.root, bg="#0b1220")
        self.container.pack(fill="both", expand=True)

        # Sidebar (Menu Lateral)
        self.menu = tk.Frame(self.container, bg="#020617", width=280)
        self.menu.pack(side="left", fill="y")
        self.menu.pack_propagate(False)

        # Área Principal (Conteúdo) - FALTAVA ISSO
        self.area = tk.Frame(self.container, bg="#0b1220")
        self.area.pack(side="right", fill="both", expand=True)

        # Logo / Título
        tk.Label(
            self.menu,
            text="PONTO CERTO",
            fg="white", bg="#020617",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(30, 10))

        # Info Usuário
        tk.Label(
            self.menu,
            text=f"Olá, {self.usuario_nome}\nPerfil: {self.perfil.upper()}",
            fg="#94a3b8", bg="#020617",
            font=("Segoe UI", 10)
        ).pack(pady=(0, 30))

        # --- BOTÕES FUNCIONAIS ---
        self.btn_individual = self.criar_botao("Gerar Folha Individual", self.abrir_individual)
        self.btn_lote = self.criar_botao("Gerar em Lote", self.abrir_lote)

        # --- LÓGICA DE ADMIN ---
        # Só mostra o botão se o perfil for 'admin'
        if self.perfil == 'admin':
            # Separador visual
            tk.Frame(self.menu, height=20, bg="#020617").pack() 
            
            # Botão diferenciado (amarelo) chamando sua classe RepositorioUsuarios
            self.btn_admin = self.criar_botao("⚙ Gestão de Usuários", self.abrir_gestao_usuarios)
            self.btn_admin.config(fg="#fbbf24", activeforeground="#fbbf24")

        # Espaço e Botão Sair (Rodapé do menu)
        tk.Frame(self.menu, height=40, bg="#020617").pack(side="bottom")
        self.criar_botao("Sair do Sistema", self.sair)

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
            height=2,
            cursor="hand2"
        )
        btn.pack(fill="x", pady=2)
        return btn

    def executar(self, nome, comando):
        self.atualizar_selecao(nome)
        
        # Se for gestão (popup), não limpa a área principal
        if "Gestão" in nome:
            comando()
        else:
            self.limpar_area()
            comando()

    def atualizar_selecao(self, nome):
        # Reseta cores
        for widget in self.menu.winfo_children():
            if isinstance(widget, tk.Button):
                # Mantém a cor especial do admin se não for ele o clicado
                if "Gestão" in widget.cget("text"):
                    widget.config(bg="#020617", fg="#fbbf24")
                else:
                    widget.config(bg="#020617", fg="#e5e7eb")

        # Destaca o clicado
        for widget in self.menu.winfo_children():
            if isinstance(widget, tk.Button) and nome in widget.cget("text"):
                widget.config(bg="#1e293b")

    def limpar_area(self):
        for w in self.area.winfo_children():
            w.destroy()

    def mostrar_home(self):
        self.limpar_area()
        # Centraliza um cartão de boas-vindas
        card = tk.Frame(self.area, bg="#020617") 
        card.place(relx=0.5, rely=0.5, anchor="center") 

        tk.Label(
            card,
            text="Bem-vindo ao Sistema Ponto Certo",
            font=("Segoe UI", 26, "bold"),
            bg="#020617", fg="white"
        ).pack(pady=(20, 10), padx=40)

        tk.Label(
            card,
            text="Plataforma corporativa para geração automática\nde folhas de ponto em PDF.",
            font=("Segoe UI", 14),
            bg="#020617", fg="#cbd5e1",
            justify="center"
        ).pack(pady=(0, 20))

    def abrir_individual(self):
        TelaGerarIndividual(self.area, self.mostrar_home)

    def abrir_lote(self):
        TelaGerarLote(self.area, self.mostrar_home)

    def abrir_gestao_usuarios(self):
        # AQUI ESTÁ A CHAMADA DA SUA CLASSE ESPECÍFICA
        # RepositorioUsuarios(self.root, self.dados_usuario) # ERRO: Isso não é uma tela
        messagebox.showinfo("Em Desenvolvimento", 
                            "A tela visual de Gestão de Usuários ainda não foi implementada.\n"
                            "A classe RepositorioUsuarios é apenas para dados.")

    def sair(self):
        if messagebox.askyesno("Sair", "Deseja fazer logout e voltar ao login?"):
            self.root.destroy()