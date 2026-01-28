import tkinter as tk
from tkinter import messagebox
from autenticacao import Autenticacao
from tela_principal import TelaPrincipal


class TelaLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("Ponto Certo - Login")
        self.root.geometry("420x320")
        self.root.resizable(False, False)

        self.auth = Autenticacao()

        # ENTER faz login
        self.root.bind("<Return>", lambda e: self.login())

        # Frame principal
        self.frame = tk.Frame(root)
        self.frame.pack(expand=True)

        # Título
        tk.Label(self.frame, text="PONTO CERTO", font=("Arial", 22, "bold")).pack(pady=(10, 2))
        tk.Label(self.frame, text="Sistema de Folha de Ponto", font=("Arial", 11)).pack(pady=(0, 20))

        # Usuário
        tk.Label(self.frame, text="Usuário:").pack(anchor="w", padx=40)
        self.user = tk.Entry(self.frame, width=30)
        self.user.pack(pady=5)

        # Senha
        tk.Label(self.frame, text="Senha:").pack(anchor="w", padx=40)
        self.senha = tk.Entry(self.frame, width=30, show="*")
        self.senha.pack(pady=5)

        # Botões
        tk.Button(self.frame, text="Entrar", width=20, command=self.login).pack(pady=(20, 5))
        tk.Button(self.frame, text="Cancelar", width=20, command=root.destroy).pack()

        # Foco inicial
        self.user.focus()

    def login(self):

        usuario = self.user.get().strip()
        senha = self.senha.get().strip()

        perfil = self.auth.validar(usuario, senha)
        if perfil:
            # Remove a tela de login
            self.frame.destroy()

            # Abre a tela principal no mesmo root
            TelaPrincipal(self.root, {'usuario': usuario, 'perfil': perfil})
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos")
            self.user.delete(0, tk.END)
            self.senha.delete(0, tk.END)
            self.user.focus()
