import tkinter as tk
from tkinter import messagebox
from tela_gerar_individual import TelaGerarIndividual
from tela_gerar_lote import TelaGerarLote
from tela_gestao_usuarios import TelaGestaoUsuarios
from tela_lancamento_ferias import TelaLancamentoFerias
from tela_gestao_funcionarios import TelaGestaoFuncionarios
from repositorio_dados import RepositorioDados

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
        
        # Configuração de Logout Automático (15 minutos)
        self.timer_id = None
        self.iniciar_monitoramento_inatividade()
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
        self.lbl_logo = tk.Label(
            self.menu,
            text="PONTO CERTO",
            fg="white", bg="#020617",
            font=("Segoe UI", 18, "bold")
        )
        self.lbl_logo.pack(pady=(30, 10))
        self.lbl_logo.bind("<Button-3>", lambda e: print("Core System developed by [SEU NOME]")) # Botão Direito do Mouse

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
        self.criar_botao("👥 Gestão de Funcionários", self.abrir_gestao_funcionarios)
        self.criar_botao("🏥 Lançar Ausências", self.abrir_lancamento_ausencias)

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
        TelaGestaoUsuarios(self.area, self.mostrar_home)

    def abrir_lancamento_ausencias(self):
        TelaLancamentoFerias(self.area, self.mostrar_home, titulo="Lançamento de Ausências")

    def abrir_gestao_funcionarios(self):
        TelaGestaoFuncionarios(self.area, self.mostrar_home)

    # --- LÓGICA DE LOGOUT AUTOMÁTICO ---
    def iniciar_monitoramento_inatividade(self):
        # 15 minutos * 60 segundos * 1000 milissegundos
        self.TEMPO_LIMITE = 15 * 60 * 1000 
        
        # Monitora qualquer movimento ou tecla na janela principal
        self.root.bind_all('<Any-KeyPress>', self.reset_timer)
        self.root.bind_all('<Any-ButtonPress>', self.reset_timer)
        self.root.bind_all('<Motion>', self.reset_timer)
        
        self.reset_timer()

    def reset_timer(self, event=None):
        # Cancela o timer anterior se existir
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        
        # Inicia um novo timer para logout
        self.timer_id = self.root.after(self.TEMPO_LIMITE, self.logout_por_inatividade)

    def logout_por_inatividade(self):
        messagebox.showwarning("Sessão Expirada", "Sua sessão foi encerrada por inatividade (15 min).")
        self._realizar_logout()

    def sair(self):
        if messagebox.askyesno("Sair", "Deseja fazer logout e voltar ao login?"):
            self._realizar_logout()

    def _realizar_logout(self):
        # Limpa o timer para não disparar depois de sair
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        
        # Remove os bindings para não afetar a tela de login
        self.root.unbind_all('<Any-KeyPress>')
        self.root.unbind_all('<Any-ButtonPress>')
        self.root.unbind_all('<Motion>')

        self.container.destroy()
        self.root.state("normal")
        self.root.configure(bg="#f0f0f0")
        
        from tela_login import TelaLogin
        TelaLogin(self.root)