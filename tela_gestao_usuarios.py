import tkinter as tk
from tkinter import messagebox, ttk
from repositorio_usuarios import RepositorioUsuarios

class TelaGestaoUsuarios:
    def __init__(self, parent, voltar_callback):
        self.parent = parent
        self.voltar = voltar_callback
        self.repo = RepositorioUsuarios()

        self.frame = tk.Frame(parent, bg="#f0f2f5")
        self.frame.pack(fill="both", expand=True)

        self.criar_layout()
        self.listar_usuarios()

    def criar_layout(self):
        # Cabeçalho
        tk.Label(self.frame, text="Gestão de Usuários",
                 font=("Segoe UI", 20, "bold"), bg="#f0f2f5").pack(pady=20)

        container = tk.Frame(self.frame, bg="#f0f2f5")
        container.pack(fill="both", expand=True, padx=40, pady=10)

        # --- COLUNA ESQUERDA: LISTA ---
        frame_lista = tk.Frame(container, bg="white")
        frame_lista.pack(side="left", fill="both", expand=True, padx=(0, 20))

        # Treeview (Tabela)
        cols = ("login", "perfil", "unidade")
        self.tree = ttk.Treeview(frame_lista, columns=cols, show="headings", selectmode="browse")
        
        self.tree.heading("login", text="Login")
        self.tree.column("login", width=120)
        
        self.tree.heading("perfil", text="Perfil")
        self.tree.column("perfil", width=80)
        
        self.tree.heading("unidade", text="Unidade")
        self.tree.column("unidade", width=150)

        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botão Excluir (Abaixo da lista)
        btn_excluir = tk.Button(frame_lista, text="Excluir Selecionado", bg="#ef4444", fg="white",
                                font=("Segoe UI", 9, "bold"), command=self.excluir,
                                bd=0, cursor="hand2", activebackground="#d32f2f", 
                                activeforeground="white")
        btn_excluir.pack(fill="x", pady=5, ipady=4)

        # --- COLUNA DIREITA: FORMULÁRIO ---
        frame_form = tk.Frame(container, bg="#e2e8f0", padx=20, pady=20)
        frame_form.pack(side="right", fill="y")

        tk.Label(frame_form, text="Novo / Editar", font=("Segoe UI", 12, "bold"), bg="#e2e8f0").pack(pady=(0, 15))

        # Login
        tk.Label(frame_form, text="Login:", bg="#e2e8f0", anchor="w").pack(fill="x")
        self.entry_login = tk.Entry(frame_form)
        self.entry_login.pack(fill="x", pady=(0, 10))

        # Senha
        tk.Label(frame_form, text="Senha:", bg="#e2e8f0", anchor="w").pack(fill="x")
        self.entry_senha = tk.Entry(frame_form, show="*")
        self.entry_senha.pack(fill="x", pady=(0, 10))

        # Perfil
        tk.Label(frame_form, text="Perfil:", bg="#e2e8f0", anchor="w").pack(fill="x")
        self.combo_perfil = ttk.Combobox(frame_form, values=["admin", "comum"], state="readonly")
        self.combo_perfil.current(1) # Default comum
        self.combo_perfil.pack(fill="x", pady=(0, 10))

        # Unidade
        tk.Label(frame_form, text="Unidade (Opcional):", bg="#e2e8f0", anchor="w").pack(fill="x")
        self.entry_unidade = tk.Entry(frame_form)
        self.entry_unidade.pack(fill="x", pady=(0, 10))

        # Botão Salvar
        tk.Button(frame_form, text="Salvar Usuário", bg="#22c55e", fg="white",
                  font=("Segoe UI", 10, "bold"), command=self.salvar,
                  bd=0, cursor="hand2", activebackground="#1e8e3e", 
                  activeforeground="white").pack(fill="x", pady=20, ipady=8)

        # Botão Voltar (Fora do container, no rodapé)
        tk.Button(self.frame, text="Voltar ao Menu", command=self.voltar,
                  bg="#6c757d", fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, cursor="hand2", activebackground="#5a6268", 
                  activeforeground="white").pack(pady=10, ipady=4, ipadx=10)

    def listar_usuarios(self):
        # Limpa a lista atual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Carrega do Repositório (Banco)
        dados = self.repo.buscar_todos()
        for login, info in dados.items():
            perfil = info.get("perfil", "comum")
            unidade = info.get("unidade", "-")
            self.tree.insert("", "end", values=(login, perfil, unidade))

    def salvar(self):
        login = self.entry_login.get().strip()
        senha = self.entry_senha.get().strip()
        perfil = self.combo_perfil.get()
        unidade = self.entry_unidade.get().strip()

        if not login or not senha:
            messagebox.showwarning("Atenção", "Login e Senha são obrigatórios.")
            return

        # Verifica se já existe (Consulta ao banco)
        usuario_existente = self.repo.buscar_por_login(login)

        if usuario_existente:
            if not messagebox.askyesno("Confirmar", f"O usuário '{login}' já existe. Deseja atualizar a senha/dados?"):
                return

        self.repo.salvar_usuario(login, senha, perfil, unidade)
        messagebox.showinfo("Sucesso", f"Usuário '{login}' salvo.")
        
        self.limpar_form()
        self.listar_usuarios()

    def excluir(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um usuário na lista para excluir.")
            return

        item = self.tree.item(selecionado[0])
        login = item['values'][0]

        if login == "admin":
            messagebox.showerror("Bloqueado", "Não é permitido excluir o administrador principal.")
            return

        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja remover o usuário '{login}'?"):
            if self.repo.excluir_usuario(login):
                self.listar_usuarios()
                messagebox.showinfo("Sucesso", "Usuário removido.")
            else:
                messagebox.showerror("Erro", "Erro ao excluir usuário.")

    def limpar_form(self):
        self.entry_login.delete(0, "end")
        self.entry_senha.delete(0, "end")
        self.entry_unidade.delete(0, "end")
        self.combo_perfil.current(1)
