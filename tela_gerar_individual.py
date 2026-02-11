import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os
import datetime
from gerador_folha import GeradorFolhaPonto
from repositorio_dados import RepositorioDados

class TelaGerarIndividual:
    def __init__(self, parent, voltar_callback):
        self.parent = parent
        self.voltar = voltar_callback
        self.repo = RepositorioDados()

        self.frame = tk.Frame(parent, bg="#f0f2f5") 
        self.frame.pack(fill="both", expand=True)

        self.funcionarios = []
        self.unidades = []
        self.lista_display_completa = []
        
        self.criar_layout()
        self.carregar_dados()

    def criar_layout(self):
        tk.Label(self.frame, text="Gerar Folha Individual",
                 font=("Segoe UI", 20, "bold"), bg="#f0f2f5").pack(pady=20)

        container = tk.Frame(self.frame, bg="#f0f2f5")
        container.pack(pady=10)

        # --- 1. SELEÇÃO DE UNIDADE (NOVO) ---
        tk.Label(container, text="Selecione a Unidade:", bg="#f0f2f5").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        
        self.combo_unidade = ttk.Combobox(container, width=55, state="readonly")
        self.combo_unidade.set("Selecione...")
        self.combo_unidade.bind("<<ComboboxSelected>>", self.filtrar_funcionarios)
        self.combo_unidade.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # --- 2. SELEÇÃO DE FUNCIONÁRIO ---
        tk.Label(container, text="Selecione o Funcionário:", bg="#f0f2f5").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        
        self.combo_func = ttk.Combobox(container, width=55, state="readonly")
        self.combo_func.set("Aguardando Unidade...")
        self.combo_func.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.combo_func.bind("<<ComboboxSelected>>", self.ao_selecionar_funcionario)
        self.combo_func.bind("<Key>", self.filtrar_por_letra)

        # --- 3. MÊS E ANO ---
        tk.Label(container, text="Mês (1-12):", bg="#f0f2f5").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.mes_var = tk.IntVar(value=datetime.datetime.now().month)
        tk.Entry(container, textvariable=self.mes_var, width=10).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        tk.Label(container, text="Ano:", bg="#f0f2f5").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.ano_var = tk.IntVar(value=datetime.datetime.now().year)
        tk.Entry(container, textvariable=self.ano_var, width=10).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # --- 4. MODELO DE FOLHA (NOVO) ---
        tk.Label(container, text="Modelo:", bg="#f0f2f5").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.var_carga = tk.StringVar(value="40h")
        frame_carga = tk.Frame(container, bg="#f0f2f5")
        frame_carga.grid(row=4, column=1, sticky="w")
        tk.Radiobutton(frame_carga, text="Padrão (40h)", variable=self.var_carga, value="40h", bg="#f0f2f5").pack(side="left")
        tk.Radiobutton(frame_carga, text="30 Horas", variable=self.var_carga, value="30h", bg="#f0f2f5").pack(side="left")
        tk.Radiobutton(frame_carga, text="Escala 12x36", variable=self.var_carga, value="12x36", bg="#f0f2f5").pack(side="left", padx=10)

        # --- 5. RECESSO ---
        tk.Button(container, text="📅 Definir Recesso (Global)", 
                  command=self.definir_recesso,
                  bg="#ff9800", fg="white", bd=0, padx=10).grid(row=5, column=0, columnspan=2, pady=10)
        
        self.lbl_recesso = tk.Label(container, text="Nenhum recesso definido", bg="#f0f2f5", fg="#666")
        self.lbl_recesso.grid(row=6, column=0, columnspan=2)

        # --- 6. TIPO DE GERAÇÃO ---
        tk.Label(container, text="Ação:", bg="#f0f2f5").grid(row=7, column=0, sticky="ne", padx=5, pady=5)
        self.tipo_var = tk.StringVar(value="impressao")
        frame_radio = tk.Frame(container, bg="#f0f2f5")
        frame_radio.grid(row=7, column=1, sticky="w")
        
        tk.Radiobutton(frame_radio, text="Imprimir (Abrir PDF)", variable=self.tipo_var, value="impressao", bg="#f0f2f5").pack(anchor="w")
        tk.Radiobutton(frame_radio, text="Salvar PDF", variable=self.tipo_var, value="envio", bg="#f0f2f5").pack(anchor="w")

        # Botões
        tk.Button(self.frame, text="CONFIRMAR GERAÇÃO", 
                  bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"),
                  command=self.gerar, width=25, bd=0, cursor="hand2", 
                  activebackground="#45a049", activeforeground="white").pack(pady=20, ipady=8)
        
        tk.Button(self.frame, text="Voltar ao Menu", command=self.voltar,
                  bg="#6c757d", fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, cursor="hand2", activebackground="#5a6268", 
                  activeforeground="white").pack(pady=5, ipady=4, ipadx=10)

    def carregar_dados(self):
        self.funcionarios = self.repo.listar_todos_funcionarios()
        
        if not self.funcionarios:
            messagebox.showwarning("Aviso", "Nenhum funcionário encontrado nos arquivos Excel configurados.")
            
        # Extrai lista única de unidades e ordena
        unidades_unicas = set(f.get('unidade', 'Sede') for f in self.funcionarios)
        self.unidades = sorted(list(unidades_unicas))

        # Popula o combo de Unidades
        self.combo_unidade['values'] = self.unidades

    def filtrar_funcionarios(self, event=None):
        """Chamado automaticamente quando a unidade muda"""
        unidade_selecionada = self.combo_unidade.get()
        
        # Filtra a lista principal
        funcs_filtrados = [f for f in self.funcionarios if f.get('unidade', 'Sede') == unidade_selecionada]
        funcs_filtrados.sort(key=lambda x: x['nome']) # Ordena por nome

        # Atualiza o combo de funcionários
        lista_display = [f"{f['nome']} ({f.get('matricula', '?')})" for f in funcs_filtrados]
        self.combo_func['values'] = lista_display
        self.lista_display_completa = lista_display
        self.combo_func.set("Selecione...")
        
        # Restaura comportamento automático: PGPL -> 30h, Outros -> 40h
        if "PGPL" in unidade_selecionada.upper():
            self.var_carga.set("30h")
        else:
            self.var_carga.set("40h")

    def ao_selecionar_funcionario(self, event=None):
        selecao = self.combo_func.get()
        if not selecao or selecao == "Selecione...": return
        
        nome_selecionado = selecao.split(" (")[0]
        func_obj = next((f for f in self.funcionarios if f["nome"] == nome_selecionado), None)
        
        if func_obj:
            if func_obj.get('escala') == '12X36':
                self.var_carga.set("12x36")
            else:
                self.var_carga.set(func_obj.get('carga_horaria', '40h'))

    def filtrar_por_letra(self, event):
        # Ignora teclas de navegação para manter o uso normal das setas
        if event.keysym in ('Up', 'Down', 'Return', 'Tab', 'Left', 'Right', 'Home', 'End'):
            return

        # Resetar filtro com Backspace ou ESC
        if event.keysym in ('BackSpace', 'Escape', 'Delete'):
            self.combo_func['values'] = self.lista_display_completa
            return

        # Filtra pela letra digitada
        if event.char and event.char.isalnum():
            letra = event.char.lower()
            filtrados = [x for x in self.lista_display_completa if x.lower().startswith(letra)]
            
            self.combo_func['values'] = filtrados
            if filtrados:
                self.combo_func.set(filtrados[0])
                self.ao_selecionar_funcionario()
                self.combo_func.event_generate('<Down>') # Reabre a lista mostrando apenas os filtrados

    def definir_recesso(self):
        """Define dias de recesso para a geração atual"""
        from tkinter import simpledialog
        # Simplificação: Pede dias separados por vírgula
        dias_str = simpledialog.askstring("Definir Recesso", "Digite os dias de recesso deste mês (ex: 24, 25, 31):")
        if dias_str:
            try:
                mes = int(self.mes_var.get())
                ano = int(self.ano_var.get())
                dias = [int(d.strip()) for d in dias_str.split(",") if d.strip().isdigit()]
                
                # Converte para formato YYYY-MM-DD para o gerador
                datas_recesso = []
                for d in dias:
                    dt = datetime.date(ano, mes, d)
                    datas_recesso.append(dt.strftime("%Y-%m-%d"))
                
                # Salva no repositório (Global)
                self.repo.salvar_recessos_globais(datas_recesso)
                self.lbl_recesso.config(text=f"Recessos: {dias_str}")
            except Exception as e:
                messagebox.showerror("Erro", f"Data inválida: {e}")

    def gerar(self):
        selecao = self.combo_func.get()
        if not selecao or selecao == "Selecione..." or selecao == "Aguardando Unidade...":
            messagebox.showwarning("Atenção", "Selecione uma Unidade e um Funcionário.")
            return

        nome_selecionado = selecao.split(" (")[0]
        func_obj = next((f for f in self.funcionarios if f["nome"] == nome_selecionado), None)
        
        if not func_obj:
            messagebox.showerror("Erro", "Funcionário não identificado nos dados.")
            return

        try:
            mes = int(self.mes_var.get())
            ano = int(self.ano_var.get())
        except ValueError:
            messagebox.showerror("Erro", "Mês e Ano devem ser números.")
            return

        # Carrega dados complementares (Férias e Recessos)
        afastamentos = self.repo.get_afastamentos()
        
        # Injeta férias no objeto funcionário (temporário para geração)
        # Filtra férias apenas deste funcionário
        minhas_ferias = [f for f in afastamentos.get('ferias', []) if f['matricula'] == func_obj['matricula']]
        func_obj['ferias'] = minhas_ferias

        # Atualiza carga horária com a seleção da tela (permite override manual)
        modelo_selecionado = self.var_carga.get()
        if modelo_selecionado == "12x36":
            func_obj['escala'] = '12X36'
        else:
            func_obj['escala'] = 'NORMAL'
            func_obj['carga_horaria'] = modelo_selecionado

        gerador = GeradorFolhaPonto()

        # --- VALIDAÇÃO ANTECIPADA ---
        try:
            gerador.validar_regras_negocio(mes, ano)
        except ValueError as ve:
            messagebox.showwarning("Bloqueio de Regra", str(ve))
            return

        # --- JANELA DE CARREGAMENTO ---
        loading_win = tk.Toplevel(self.parent)
        loading_win.title("Processando")
        loading_win.geometry("300x120")
        loading_win.resizable(False, False)
        loading_win.transient(self.parent) # Fica sempre por cima da janela pai
        loading_win.grab_set() # Bloqueia interação com a janela principal
        
        # Centralizar visualmente (simplificado)
        loading_win.geometry("+%d+%d" % (self.parent.winfo_rootx() + 50, self.parent.winfo_rooty() + 50))

        tk.Label(loading_win, text="Gerando Folha de Ponto...\nPor favor, aguarde.", font=("Segoe UI", 10)).pack(pady=15)
        pb = ttk.Progressbar(loading_win, mode='indeterminate')
        pb.pack(fill="x", padx=20, pady=5)
        pb.start(10) # Animação
        loading_win.update() # Força a renderização antes de travar no processo

        # BLOCO DE TENTATIVA DE GERAÇÃO (Captura regras de negócio)
        try:
            if self.tipo_var.get() == "impressao":
                import tempfile
                temp_dir = tempfile.gettempdir()
                caminho_pdf = os.path.join(temp_dir, f"Ponto_{func_obj['nome']}_{mes}_{ano}.pdf")
                
                self.parent.config(cursor="wait")
                self.parent.update()
                
                gerador.gerar(func_obj, mes, ano, caminho_pdf, recessos_globais=afastamentos.get('recessos', []))
                os.startfile(caminho_pdf)
            
            else: # envio/salvar
                caminho_pdf = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF", "*.pdf")],
                    initialfile=f"Ponto_{func_obj['nome']}_{mes}_{ano}.pdf",
                    title="Salvar Folha de Ponto"
                )
                if not caminho_pdf: return
                
                self.parent.config(cursor="wait")
                self.parent.update()
                
                gerador.gerar(func_obj, mes, ano, caminho_pdf, recessos_globais=afastamentos.get('recessos', []))
                messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{caminho_pdf}")

        except ValueError as ve:
            # Captura os erros de regra de negócio (data retroativa, dia 20, etc)
            messagebox.showwarning("Bloqueio de Regra", str(ve))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro crítico na geração: {e}")
        finally:
            loading_win.destroy() # Fecha a janela de carregamento
            self.parent.config(cursor="")