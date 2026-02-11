import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from repositorio_dados import RepositorioDados

class TelaLancamentoFerias:
    def __init__(self, parent, voltar_callback, titulo="Lançamento de Férias"):
        self.parent = parent
        self.voltar = voltar_callback
        self.titulo_tela = titulo
        self.repo = RepositorioDados()
        
        self.frame = tk.Frame(parent, bg="#f0f2f5")
        self.frame.pack(fill="both", expand=True)
        
        self.funcionarios = []
        
        self.criar_layout()
        self.carregar_dados()

    def criar_layout(self):
        tk.Label(self.frame, text=self.titulo_tela, 
                 font=("Segoe UI", 20, "bold"), bg="#f0f2f5").pack(pady=20)

        container = tk.Frame(self.frame, bg="#f0f2f5")
        container.pack(pady=10)

        # --- SELEÇÃO ---
        tk.Label(container, text="Unidade:", bg="#f0f2f5").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.combo_unidade = ttk.Combobox(container, width=30, state="readonly")
        self.combo_unidade.grid(row=0, column=1, padx=5, pady=5)
        self.combo_unidade.bind("<<ComboboxSelected>>", self.filtrar_funcionarios)

        tk.Label(container, text="Funcionário:", bg="#f0f2f5").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.combo_func = ttk.Combobox(container, width=30, state="readonly")
        self.combo_func.grid(row=1, column=1, padx=5, pady=5)
        self.combo_func.bind("<<ComboboxSelected>>", self.atualizar_info_atual)

        # --- TIPO ---
        tk.Label(container, text="Tipo:", bg="#f0f2f5").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.combo_tipo = ttk.Combobox(container, values=["Férias", "Atestado Médico", "Licença", "Outros"], state="readonly", width=27)
        self.combo_tipo.set("Férias") # Padrão
        self.combo_tipo.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # --- DATAS ---
        tk.Label(container, text="Data Início (DD/MM/AAAA):", bg="#f0f2f5").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_inicio = tk.Entry(container, width=15)
        self.entry_inicio.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        tk.Label(container, text="Data Fim (DD/MM/AAAA):", bg="#f0f2f5").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.entry_fim = tk.Entry(container, width=15)
        self.entry_fim.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # --- INFO ATUAL ---
        self.lbl_info = tk.Label(container, text="", bg="#f0f2f5", fg="#666")
        self.lbl_info.grid(row=5, column=0, columnspan=2, pady=10)

        # --- BOTÕES ---
        btn_frame = tk.Frame(self.frame, bg="#f0f2f5")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="SALVAR", command=self.salvar,
                  bg="#2196F3", fg="white", font=("Segoe UI", 10, "bold"),
                  width=20, bd=0, cursor="hand2").pack(side="left", padx=10)

        tk.Button(btn_frame, text="Voltar", command=self.voltar,
                  bg="#6c757d", fg="white", font=("Segoe UI", 10),
                  width=10, bd=0, cursor="hand2").pack(side="left", padx=10)

    def carregar_dados(self):
        self.funcionarios = self.repo.listar_todos_funcionarios()
        unidades = sorted(list(set(f.get('unidade', 'Sede') for f in self.funcionarios)))
        self.combo_unidade['values'] = unidades

    def filtrar_funcionarios(self, event=None):
        unidade = self.combo_unidade.get()
        funcs = [f for f in self.funcionarios if f.get('unidade', 'Sede') == unidade]
        funcs.sort(key=lambda x: x['nome'])
        self.combo_func['values'] = [f"{f['nome']} ({f['matricula']})" for f in funcs]
        self.combo_func.set("")

    def atualizar_info_atual(self, event=None):
        # Busca se já tem férias cadastradas para mostrar
        matricula = self.obter_matricula_selecionada()
        if not matricula: return

        afastamentos = self.repo.get_afastamentos()
        minhas_ferias = [f for f in afastamentos.get('ferias', []) if f['matricula'] == matricula]
        
        if minhas_ferias:
            # Pega a última cadastrada
            ult = minhas_ferias[-1]
            # Converte YYYY-MM-DD para DD/MM/AAAA para exibição
            tipo = ult.get('tipo', 'Férias')
            try:
                ini = datetime.strptime(ult['inicio'], "%Y-%m-%d").strftime("%d/%m/%Y")
                fim = datetime.strptime(ult['fim'], "%Y-%m-%d").strftime("%d/%m/%Y")
                self.lbl_info.config(text=f"Último: {tipo} ({ini} até {fim})")
            except:
                self.lbl_info.config(text="Erro ao ler datas anteriores.")
        else:
            self.lbl_info.config(text="Nenhum registro de férias encontrado.")

    def obter_matricula_selecionada(self):
        selecao = self.combo_func.get()
        if not selecao: return None
        # Formato "Nome (Matricula)"
        return selecao.split("(")[-1].replace(")", "")

    def salvar(self):
        matricula = self.obter_matricula_selecionada()
        if not matricula:
            messagebox.showwarning("Aviso", "Selecione um funcionário.")
            return

        ini_str = self.entry_inicio.get()
        fim_str = self.entry_fim.get()
        tipo = self.combo_tipo.get()

        try:
            # Valida e converte para YYYY-MM-DD (formato ISO para JSON)
            ini_iso = datetime.strptime(ini_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            fim_iso = datetime.strptime(fim_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            
            self.repo.salvar_afastamento(matricula, ini_iso, fim_iso, tipo)
            messagebox.showinfo("Sucesso", f"{tipo} registrado(a) com sucesso!")
            self.atualizar_info_atual()
        except ValueError:
            messagebox.showerror("Erro", "Datas inválidas.\nUse o formato DD/MM/AAAA (ex: 01/02/2026).")