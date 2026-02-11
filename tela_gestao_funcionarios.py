import tkinter as tk
from tkinter import messagebox, ttk
from repositorio_dados import RepositorioDados

class TelaGestaoFuncionarios:
    def __init__(self, parent, voltar_callback):
        self.parent = parent
        self.voltar = voltar_callback
        self.repo = RepositorioDados()

        self.frame = tk.Frame(parent, bg="#f0f2f5")
        self.frame.pack(fill="both", expand=True)
        
        self.matricula_em_edicao = None # Controle de estado (Novo vs Edição)

        self.criar_layout()
        self.listar_funcionarios()

    def criar_layout(self):
        # Cabeçalho
        tk.Label(self.frame, text="Gestão de Funcionários (Excel)",
                 font=("Segoe UI", 20, "bold"), bg="#f0f2f5").pack(pady=20)

        container = tk.Frame(self.frame, bg="#f0f2f5")
        container.pack(fill="both", expand=True, padx=40, pady=10)

        # --- COLUNA ESQUERDA: LISTA ---
        frame_lista = tk.Frame(container, bg="white")
        frame_lista.pack(side="left", fill="both", expand=True, padx=(0, 20))

        cols = ("nome", "matricula", "cargo", "escala", "carga")
        self.tree = ttk.Treeview(frame_lista, columns=cols, show="headings", selectmode="browse")
        
        self.tree.heading("nome", text="Nome")
        self.tree.column("nome", width=200)
        
        self.tree.heading("matricula", text="Matrícula")
        self.tree.column("matricula", width=100)
        
        self.tree.heading("cargo", text="Cargo")
        self.tree.column("cargo", width=150)

        self.tree.heading("escala", text="Escala")
        self.tree.column("escala", width=80)

        self.tree.heading("carga", text="Carga H.")
        self.tree.column("carga", width=80)

        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Evento de clique na lista
        self.tree.bind("<<TreeviewSelect>>", self.ao_selecionar)

        # Botão Excluir
        btn_excluir = tk.Button(frame_lista, text="🗑 Excluir Selecionado", bg="#ef4444", fg="white",
                                font=("Segoe UI", 9, "bold"), command=self.excluir,
                                bd=0, cursor="hand2")
        btn_excluir.pack(fill="x", pady=5, ipady=4)

        # --- COLUNA DIREITA: FORMULÁRIO ---
        frame_form = tk.Frame(container, bg="#e2e8f0", padx=20, pady=20)
        frame_form.pack(side="right", fill="y")

        self.lbl_form = tk.Label(frame_form, text="Novo Funcionário", font=("Segoe UI", 12, "bold"), bg="#e2e8f0")
        self.lbl_form.pack(pady=(0, 15))

        # Campos
        tk.Label(frame_form, text="Nome Completo:", bg="#e2e8f0", anchor="w").pack(fill="x")
        self.entry_nome = tk.Entry(frame_form)
        self.entry_nome.pack(fill="x", pady=(0, 10))

        tk.Label(frame_form, text="Matrícula:", bg="#e2e8f0", anchor="w").pack(fill="x")
        self.entry_matricula = tk.Entry(frame_form)
        self.entry_matricula.pack(fill="x", pady=(0, 10))

        tk.Label(frame_form, text="Cargo:", bg="#e2e8f0", anchor="w").pack(fill="x")
        self.entry_cargo = tk.Entry(frame_form)
        self.entry_cargo.pack(fill="x", pady=(0, 10))

        tk.Label(frame_form, text="Escala:", bg="#e2e8f0", anchor="w").pack(fill="x")
        self.combo_escala = ttk.Combobox(frame_form, values=["NORMAL", "12X36"], state="readonly")
        self.combo_escala.set("NORMAL")
        self.combo_escala.pack(fill="x", pady=(0, 10))

        tk.Label(frame_form, text="Carga Horária:", bg="#e2e8f0", anchor="w").pack(fill="x")
        self.combo_carga = ttk.Combobox(frame_form, values=["40h", "30h"], state="readonly")
        self.combo_carga.set("40h")
        self.combo_carga.pack(fill="x", pady=(0, 10))

        # Botões Ação
        self.btn_salvar = tk.Button(frame_form, text="💾 Salvar", bg="#22c55e", fg="white",
                  font=("Segoe UI", 10, "bold"), command=self.salvar,
                  bd=0, cursor="hand2")
        self.btn_salvar.pack(fill="x", pady=10, ipady=5)
        
        tk.Button(frame_form, text="Limpar / Novo", bg="#94a3b8", fg="white",
                  font=("Segoe UI", 9), command=self.limpar_form,
                  bd=0, cursor="hand2").pack(fill="x", pady=5)

        # Botão Voltar
        tk.Button(self.frame, text="Voltar ao Menu", command=self.voltar,
                  bg="#6c757d", fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, cursor="hand2").pack(pady=10, ipady=4, ipadx=10)

    def listar_funcionarios(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        funcionarios = self.repo.listar_todos_funcionarios()
        for f in funcionarios:
            self.tree.insert("", "end", values=(f['nome'], f['matricula'], f['cargo'], f.get('escala', 'NORMAL'), f.get('carga_horaria', '40h')))

    def ao_selecionar(self, event):
        selecionado = self.tree.selection()
        if not selecionado: return
        
        item = self.tree.item(selecionado[0])
        vals = item['values'] # (nome, matricula, cargo, escala, carga)
        
        self.entry_nome.delete(0, "end"); self.entry_nome.insert(0, vals[0])
        self.entry_matricula.delete(0, "end"); self.entry_matricula.insert(0, str(vals[1]))
        self.entry_cargo.delete(0, "end"); self.entry_cargo.insert(0, vals[2])
        self.combo_escala.set(vals[3])
        if len(vals) > 4:
            self.combo_carga.set(vals[4])
        
        self.matricula_em_edicao = str(vals[1])
        self.lbl_form.config(text="Editando Funcionário")
        self.btn_salvar.config(text="🔄 Atualizar")

    def limpar_form(self):
        self.entry_nome.delete(0, "end")
        self.entry_matricula.delete(0, "end")
        self.entry_cargo.delete(0, "end")
        self.combo_escala.set("NORMAL")
        self.combo_carga.set("40h")
        self.matricula_em_edicao = None
        self.lbl_form.config(text="Novo Funcionário")
        self.btn_salvar.config(text="💾 Salvar")
        self.tree.selection_remove(self.tree.selection())

    def salvar(self):
        nome, mat, cargo = self.entry_nome.get(), self.entry_matricula.get(), self.entry_cargo.get()
        escala, carga = self.combo_escala.get(), self.combo_carga.get()
        if not nome or not mat: return messagebox.showwarning("Atenção", "Nome e Matrícula obrigatórios.")

        if self.matricula_em_edicao:
            ok, msg = self.repo.editar_funcionario(self.matricula_em_edicao, nome, mat, cargo, escala, carga)
        else:
            ok, msg = self.repo.adicionar_funcionario(nome, mat, cargo, escala, carga)

        if ok: messagebox.showinfo("Sucesso", msg); self.limpar_form(); self.listar_funcionarios()
        else: messagebox.showerror("Erro", msg)

    def excluir(self):
        sel = self.tree.selection()
        if not sel: return messagebox.showwarning("Atenção", "Selecione para excluir.")
        mat = str(self.tree.item(sel[0])['values'][1])
        if messagebox.askyesno("Confirmar", "Excluir funcionário?"):
            ok, msg = self.repo.excluir_funcionario(mat)
            if ok: self.limpar_form(); self.listar_funcionarios()
            else: messagebox.showerror("Erro", msg)