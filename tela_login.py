import tkinter as tk
from tkinter import messagebox
from autenticacao import Autenticacao
from tela_principal import TelaPrincipal


class TelaLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("Ponto Certo - Login")
        
        # Configuração de Tela Cheia e Cores
        self.root.state("zoomed")
        self.root.configure(bg="#0f172a") # Fundo escuro (Slate 900)

        self.auth = Autenticacao()

        # ENTER faz login
        self.root.bind("<Return>", lambda e: self.login())

        self.criar_layout()

    def criar_layout(self):
        # --- CARTÃO CENTRAL (Login Box) ---
        # Cria um frame branco centralizado
        self.card = tk.Frame(self.root, bg="white", padx=40, pady=40)
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        # Sombra visual (opcional, simulada com borda)
        self.card.configure(highlightbackground="#cbd5e1", highlightthickness=1)

        # Título
        tk.Label(self.card, text="PONTO CERTO", font=("Segoe UI", 24, "bold"), bg="white", fg="#1e293b").pack(pady=(0, 5))
        tk.Label(self.card, text="Acesso ao Sistema", font=("Segoe UI", 11), bg="white", fg="#64748b").pack(pady=(0, 30))

        # Usuário
        tk.Label(self.card, text="Usuário", font=("Segoe UI", 10, "bold"), bg="white", fg="#334155").pack(anchor="w")
        self.user = tk.Entry(self.card, width=35, font=("Segoe UI", 11), bd=1, relief="solid")
        self.user.pack(pady=(5, 15), ipady=3)

        # Senha
        tk.Label(self.card, text="Senha", font=("Segoe UI", 10, "bold"), bg="white", fg="#334155").pack(anchor="w")
        self.senha = tk.Entry(self.card, width=35, font=("Segoe UI", 11), bd=1, relief="solid", show="*")
        self.senha.pack(pady=(5, 25), ipady=3)

        # Botões
        btn_entrar = tk.Button(self.card, text="ENTRAR NO SISTEMA", width=30, command=self.login,
                               bg="#2196F3", fg="white", font=("Segoe UI", 10, "bold"),
                               bd=0, relief="flat", activebackground="#1976D2", 
                               activeforeground="white", cursor="hand2")
        btn_entrar.pack(pady=(0, 10), ipady=8)

        btn_sair = tk.Button(self.card, text="Sair", width=30, command=self.root.destroy,
                             bg="white", fg="#64748b", font=("Segoe UI", 9),
                             bd=0, relief="flat", activebackground="#f1f5f9",
                             activeforeground="#0f172a", cursor="hand2")
        btn_sair.pack(ipady=5)
        
        # Rodapé (Fora do Card)
        tk.Label(self.root, text="© 2026 Associação Municipal de Apoio Comunitário", 
                 bg="#0f172a", fg="#475569", font=("Segoe UI", 8)).pack(side="bottom", pady=10)

        # Foco inicial
        self.user.focus()

    def login(self):

        usuario = self.user.get().strip()
        senha = self.senha.get().strip()

        # --- ASSINATURA IMPLÍCITA (EASTER EGG) ---
        if usuario.lower() == "dev" and senha == "42":
            messagebox.showinfo("Créditos", "Feito pelo melhor. Lucas S")
            return

        perfil = self.auth.validar(usuario, senha)
        if perfil:
            # Remove a tela de login
            self.card.destroy() # Destroi o card
            # Limpa qualquer outro widget que tenha sobrado no root (como o rodapé)
            for widget in self.root.winfo_children():
                widget.destroy()

            # Abre a tela principal no mesmo root
            TelaPrincipal(self.root, {'usuario': usuario, 'perfil': perfil})
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos")
            self.user.delete(0, tk.END)
            self.senha.delete(0, tk.END)
            self.user.focus()
