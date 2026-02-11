import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os
import zipfile
import tempfile
import datetime
import time
from gerador_folha import GeradorFolhaPonto
from repositorio_dados import RepositorioDados

class TelaGerarLote:
    def __init__(self, parent, voltar_callback):
        self.parent = parent
        self.voltar = voltar_callback

        self.frame = tk.Frame(parent, bg="#e5e7eb")
        self.frame.pack(fill="both", expand=True)

        self.repo = RepositorioDados()
        self.vars = [] 
        self.funcionarios = []
        self.criar_layout()
        self.carregar_funcionarios()

    def criar_layout(self):
        # Cabeçalho
        header = tk.Frame(self.frame, bg="#e5e7eb")
        header.pack(fill="x", pady=10)
        tk.Label(header, text="Gerar Folhas em Lote (Por Unidade)", font=("Segoe UI", 18, "bold"), bg="#e5e7eb").pack()

        # --- PAINEL DE CONTROLE (FILTRO + DATA) ---
        frame_controles = tk.Frame(self.frame, bg="#e5e7eb")
        frame_controles.pack(fill="x", padx=20, pady=5)

        # 1. Filtro
        frame_filtro = tk.Frame(frame_controles, bg="#e5e7eb")
        frame_filtro.pack(side="left", fill="x", expand=True)
        
        tk.Label(frame_filtro, text="Filtrar:", bg="#e5e7eb", font=("Arial", 10, "bold")).pack(side="left")
        self.busca = tk.StringVar()
        self.busca.trace("w", self.filtrar)
        tk.Entry(frame_filtro, textvariable=self.busca, width=20).pack(side="left", padx=5)

        # Filtro Unidade (Setor)
        tk.Label(frame_filtro, text="Setor:", bg="#e5e7eb", font=("Arial", 10, "bold")).pack(side="left", padx=(10, 0))
        self.filtro_unidade = ttk.Combobox(frame_filtro, state="readonly", width=20)
        self.filtro_unidade.set("Todas")
        self.filtro_unidade.bind("<<ComboboxSelected>>", self.filtrar)
        self.filtro_unidade.pack(side="left", padx=5)

        # Filtro Carga Horária
        tk.Label(frame_filtro, text="Carga:", bg="#e5e7eb", font=("Arial", 10, "bold")).pack(side="left", padx=(10, 0))
        self.filtro_carga = ttk.Combobox(frame_filtro, values=["Todas", "40h", "30h", "12x36"], state="readonly", width=8)
        self.filtro_carga.set("Todas")
        self.filtro_carga.bind("<<ComboboxSelected>>", self.filtrar)
        self.filtro_carga.pack(side="left", padx=5)

        # 2. Seletor de Mês e Ano
        frame_data = tk.Frame(frame_controles, bg="#e5e7eb")
        frame_data.pack(side="right")

        tk.Label(frame_data, text="Mês:", bg="#e5e7eb", font=("Arial", 10, "bold")).pack(side="left")
        self.mes_var = tk.IntVar(value=datetime.datetime.now().month)
        tk.Entry(frame_data, textvariable=self.mes_var, width=5).pack(side="left", padx=5)

        tk.Label(frame_data, text="Ano:", bg="#e5e7eb", font=("Arial", 10, "bold")).pack(side="left")
        self.ano_var = tk.IntVar(value=datetime.datetime.now().year)
        tk.Entry(frame_data, textvariable=self.ano_var, width=8).pack(side="left", padx=5)

        # --- ÁREA DE LISTA COM SCROLL ---
        frame_lista_container = tk.Frame(self.frame, bd=1, relief="sunken")
        frame_lista_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.canvas = tk.Canvas(frame_lista_container, bg="white")
        scrollbar = tk.Scrollbar(frame_lista_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Scroll do Mouse
        frame_lista_container.bind('<Enter>', self._bound_to_mousewheel)
        frame_lista_container.bind('<Leave>', self._unbound_to_mousewheel)

        # Botões de Ação
        frame_botoes = tk.Frame(self.frame, bg="#e5e7eb")
        frame_botoes.pack(fill="x", pady=20, padx=20)

        # Botões de Seleção
        frame_sel = tk.Frame(self.frame, bg="#e5e7eb")
        frame_sel.pack(fill="x", padx=20, pady=(0, 10))
        tk.Button(frame_sel, text="Marcar Ativos Visíveis", command=lambda: self.toggle_ativos(True), 
                  font=("Segoe UI", 8), bg="#d1d5db", bd=0, cursor="hand2", padx=5, pady=2,
                  activebackground="#9ca3af", activeforeground="black").pack(side="left", padx=2)
        tk.Button(frame_sel, text="Desmarcar Visíveis", command=lambda: self.toggle_all(False), 
                  font=("Segoe UI", 8), bg="#d1d5db", bd=0, cursor="hand2", padx=5, pady=2,
                  activebackground="#9ca3af", activeforeground="black").pack(side="left", padx=2)

        # Botões de Ação Principais
        frame_acoes_principais = tk.Frame(frame_botoes, bg="#e5e7eb")
        frame_acoes_principais.pack(side="left", expand=True, fill="x")

        tk.Button(frame_acoes_principais, text="Gerar Impressão (Pastas)", command=lambda: self.gerar("impressao"), 
                  bg="#2196F3", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                  activebackground="#1976D2", activeforeground="white").pack(side="left", padx=5, ipady=8)
        
        tk.Button(frame_acoes_principais, text="Gerar ZIP (Organizado)", command=lambda: self.gerar("envio"), 
                  bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                  activebackground="#45a049", activeforeground="white").pack(side="left", padx=5, ipady=8)
        
        tk.Button(frame_botoes, text="Voltar ao Menu", command=self.voltar,
                  bg="#6c757d", fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, cursor="hand2", activebackground="#5a6268", 
                  activeforeground="white").pack(side="right", ipady=4, ipadx=10)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def carregar_funcionarios(self):
        try:
            self.funcionarios = self.repo.listar_todos_funcionarios()
            
            # Ordena: Unidade -> Nome
            self.funcionarios.sort(key=lambda x: (x.get('unidade', 'Sede'), x['nome']))

            # Popula o filtro de Unidades
            unidades_unicas = sorted(list(set(f.get('unidade', 'Geral') for f in self.funcionarios)))
            self.filtro_unidade['values'] = ["Todas"] + unidades_unicas
            if not self.filtro_unidade.get():
                self.filtro_unidade.set("Todas")

            # Inicializa Vars
            for f in self.funcionarios:
                # Se não tiver status definido (legado), assume Ativo
                if 'status' not in f:
                    f['status'] = 'Ativo'
                
                status = f['status']
                # Só marca automaticamente se for 'Ativo'. Afastados/Desligados vêm desmarcados.
                is_ativo = (status == 'Ativo')
                self.vars.append((f, tk.BooleanVar(value=is_ativo)))

            self.atualizar_lista(self.funcionarios)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar funcionários: {e}")

    def atualizar_lista(self, lista_filtrada):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        last_unidade = None
        
        for f in lista_filtrada:
            unidade_atual = f.get('unidade', 'Geral')
            status = f.get('status', 'Ativo')
            
            # Separador de Unidade
            if unidade_atual != last_unidade:
                lbl_separador = tk.Label(self.scrollable_frame, text=f"--- {unidade_atual.upper()} ---", 
                                         bg="#f0f0f0", fg="#333", font=("Arial", 9, "bold"), anchor="w")
                lbl_separador.pack(fill="x", padx=2, pady=(10, 2))
                last_unidade = unidade_atual

            # Encontra a var correspondente
            par = next((p for p in self.vars if p[0]["matricula"] == f["matricula"]), None)
            if par:
                func, var = par
                
                # Visual
                cor_texto = "black"
                texto_extra = ""
                if status == "Desligado":
                    cor_texto = "red"
                    texto_extra = " (DESLIGADO)"
                elif status == "Férias":
                    cor_texto = "#FFA500"
                    texto_extra = " (FÉRIAS)"
                elif status == "Afastado":
                    cor_texto = "purple"
                    texto_extra = " (AFASTADO)"
                
                # Mostra carga horária se for 30h para diferenciar
                if func.get('carga_horaria') == '30h':
                    texto_extra += " [30h]"
                if func.get('escala') == '12X36':
                    texto_extra += " [12x36]"

                texto_display = f"{func['nome']}{texto_extra}"
                cb = tk.Checkbutton(self.scrollable_frame, text=texto_display, 
                                    variable=var, bg="white", fg=cor_texto, anchor="w")
                cb.pack(fill="x", padx=10)

    def toggle_all(self, state):
        # Altera apenas os itens visíveis pelo filtro
        termo = self.busca.get().lower()
        for f, var in self.vars:
             if self.match_filtro(f, termo):
                 var.set(state)

    def toggle_ativos(self, state):
        # Altera apenas os itens visíveis que não estão "Desligado"
        termo = self.busca.get().lower()
        for f, var in self.vars:
             if self.match_filtro(f, termo) and f.get('status') != "Desligado":
                var.set(state)

    def match_filtro(self, f, termo):
        unidade = f.get('unidade', '').lower()
        match_texto = termo in f["nome"].lower() or termo in f["matricula"] or termo in unidade
        
        # Filtro de Unidade
        unidade_selecionada = self.filtro_unidade.get()
        if not unidade_selecionada: unidade_selecionada = "Todas"
        
        match_unidade = True
        if unidade_selecionada != "Todas":
            match_unidade = (f.get('unidade', 'Geral') == unidade_selecionada)

        carga_selecionada = self.filtro_carga.get()
        if not carga_selecionada: carga_selecionada = "Todas"
        
        match_carga = True
        if carga_selecionada != "Todas":
            if carga_selecionada == "12x36":
                match_carga = (str(f.get('escala', '')).upper() == '12X36')
            else:
                f_carga = f.get('carga_horaria', '40h')
                match_carga = (f_carga == carga_selecionada)
            
        return match_texto and match_carga and match_unidade

    def filtrar(self, *args):
        termo = self.busca.get().lower()
        filtrados = [f for f, _ in self.vars if self.match_filtro(f, termo)]
        self.atualizar_lista(filtrados)

    def gerar(self, tipo):
        selecionados = [f for f, v in self.vars if v.get()]
        if not selecionados:
            messagebox.showwarning("Atenção", "Nenhum funcionário selecionado.")
            return

        # Pega a Data dos Campos de Entrada
        try:
            mes = int(self.mes_var.get())
            ano = int(self.ano_var.get())
        except ValueError:
            messagebox.showerror("Erro", "Mês e Ano devem ser números válidos.")
            return
        
        try:
            gerador = GeradorFolhaPonto()
            # Valida regra de negócio (Dia 20)
            gerador.validar_regras_negocio(mes, ano) 
        except ValueError as ve:
            messagebox.showwarning("Bloqueio de Regra", str(ve))
            return
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivos de modelo não encontrados.")
            return

        # Carrega dados complementares (Férias e Recessos)
        afastamentos = self.repo.get_afastamentos()
        recessos = afastamentos.get('recessos', [])
        lista_ferias = afastamentos.get('ferias', [])

        self.parent.config(cursor="wait")
        self.parent.update()

        # --- JANELA DE PROGRESSO ---
        total_items = len(selecionados)
        loading_win = tk.Toplevel(self.parent)
        loading_win.title("Gerando em Lote")
        loading_win.geometry("350x150")
        loading_win.resizable(False, False)
        loading_win.transient(self.parent)
        loading_win.grab_set()
        loading_win.geometry("+%d+%d" % (self.parent.winfo_rootx() + 50, self.parent.winfo_rooty() + 50))

        lbl_status = tk.Label(loading_win, text=f"Iniciando... (0/{total_items})", font=("Segoe UI", 10))
        lbl_status.pack(pady=15)
        
        pb = ttk.Progressbar(loading_win, orient="horizontal", length=300, mode="determinate", maximum=total_items)
        pb.pack(pady=10)

        try:
            if tipo == "impressao":
                pasta_raiz = filedialog.askdirectory(title="Onde salvar as pastas?")
                if not pasta_raiz: 
                    self.parent.config(cursor="")
                    return

                count = 0
                erros = []
                for i, f in enumerate(selecionados):
                    # Atualiza Progresso
                    lbl_status.config(text=f"Processando: {f['nome']}\n({i+1}/{total_items})")
                    pb['value'] = i + 1
                    loading_win.update() # Atualiza a tela

                    unidade = f.get('unidade', 'Geral').strip()
                    pasta_unidade = os.path.join(pasta_raiz, unidade)
                    os.makedirs(pasta_unidade, exist_ok=True)

                    nome_arq = f"{f['nome'].replace(' ', '_')}_{mes}_{ano}.pdf"
                    caminho = os.path.join(pasta_unidade, nome_arq)
                    
                    # Injeta férias
                    f['ferias'] = [x for x in lista_ferias if x['matricula'] == f['matricula']]

                    try:
                        gerador.gerar(f, mes, ano, caminho, recessos_globais=recessos)
                        time.sleep(0.5) # Pausa técnica para estabilidade do Word/PDF
                        count += 1
                    except Exception as e:
                        erros.append(f"{f['nome']}: {e}")
                
                msg = f"{count} folhas geradas em:\n{pasta_raiz}"
                if erros: msg += "\n\nErros:\n" + "\n".join(erros)
                messagebox.showinfo("Relatório", msg)

            else: # ZIP
                caminho_zip = filedialog.asksaveasfilename(
                    defaultextension=".zip", 
                    filetypes=[("ZIP", "*.zip")], 
                    title="Salvar ZIP",
                    initialfile=f"Folhas_{mes}_{ano}.zip"
                )
                if not caminho_zip: 
                    self.parent.config(cursor="")
                    return

                with tempfile.TemporaryDirectory() as temp_dir:
                    arquivos_zip = []
                    for i, f in enumerate(selecionados):
                        # Atualiza Progresso
                        lbl_status.config(text=f"Processando: {f['nome']}\n({i+1}/{total_items})")
                        pb['value'] = i + 1
                        loading_win.update()

                        unidade = f.get('unidade', 'Geral').strip()
                        pasta_u_temp = os.path.join(temp_dir, unidade)
                        os.makedirs(pasta_u_temp, exist_ok=True)

                        nome_arq = f"{f['nome'].replace(' ', '_')}.pdf"
                        caminho_abs = os.path.join(pasta_u_temp, nome_arq)
                        
                        # Injeta férias
                        f['ferias'] = [x for x in lista_ferias if x['matricula'] == f['matricula']]

                        try:
                            gerador.gerar(f, mes, ano, caminho_abs, recessos_globais=recessos)
                            time.sleep(0.5) # Pausa técnica para estabilidade
                            relativo = os.path.join(unidade, nome_arq)
                            arquivos_zip.append((caminho_abs, relativo))
                        except Exception as e:
                            print(f"Erro {f['nome']}: {e}")

                    with zipfile.ZipFile(caminho_zip, 'w') as zipf:
                        for abs_p, rel_p in arquivos_zip:
                            zipf.write(abs_p, arcname=rel_p)
                
                messagebox.showinfo("Sucesso", f"ZIP gerado com {len(arquivos_zip)} arquivos.")

        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Falha: {e}")
        finally:
            loading_win.destroy()
            self.parent.config(cursor="")