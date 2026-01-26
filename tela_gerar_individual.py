import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import datetime
from gerador_folha import GeradorFolhaPonto

class TelaGerarIndividual:
    def __init__(self, parent, voltar_callback):
        self.parent = parent
        self.voltar = voltar_callback

        self.frame = tk.Frame(parent, bg="#f0f2f5") 
        self.frame.pack(fill="both", expand=True)

        self.funcionarios = []
        self.unidades = []
        
        self.criar_layout()
        self.carregar_dados()

    def criar_layout(self):
        tk.Label(self.frame, text="Gerar Folha Individual",
                 font=("Segoe UI", 20, "bold"), bg="#f0f2f5").pack(pady=20)

        container = tk.Frame(self.frame, bg="#f0f2f5")
        container.pack(pady=10)

        # --- 1. SELEÇÃO DE UNIDADE (NOVO) ---
        tk.Label(container, text="Selecione a Unidade:", bg="#f0f2f5").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        
        self.unidade_var = tk.StringVar(self.frame)
        self.unidade_var.set("Selecione...")
        self.unidade_var.trace("w", self.filtrar_funcionarios) # Quando mudar, chama o filtro

        self.combo_unidade = tk.OptionMenu(container, self.unidade_var, "")
        self.combo_unidade.config(width=30)
        self.combo_unidade.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # --- 2. SELEÇÃO DE FUNCIONÁRIO ---
        tk.Label(container, text="Selecione o Funcionário:", bg="#f0f2f5").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        
        self.func_var = tk.StringVar(self.frame)
        self.func_var.set("Aguardando Unidade...")
        
        self.combo_func = tk.OptionMenu(container, self.func_var, "")
        self.combo_func.config(width=30)
        self.combo_func.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # --- 3. MÊS E ANO ---
        tk.Label(container, text="Mês (1-12):", bg="#f0f2f5").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.mes_var = tk.IntVar(value=datetime.datetime.now().month)
        tk.Entry(container, textvariable=self.mes_var, width=10).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        tk.Label(container, text="Ano:", bg="#f0f2f5").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.ano_var = tk.IntVar(value=datetime.datetime.now().year)
        tk.Entry(container, textvariable=self.ano_var, width=10).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # --- 4. TIPO DE GERAÇÃO ---
        tk.Label(container, text="Ação:", bg="#f0f2f5").grid(row=4, column=0, sticky="ne", padx=5, pady=5)
        self.tipo_var = tk.StringVar(value="impressao")
        frame_radio = tk.Frame(container, bg="#f0f2f5")
        frame_radio.grid(row=4, column=1, sticky="w")
        
        tk.Radiobutton(frame_radio, text="Imprimir (Abrir PDF)", variable=self.tipo_var, value="impressao", bg="#f0f2f5").pack(anchor="w")
        tk.Radiobutton(frame_radio, text="Salvar PDF", variable=self.tipo_var, value="envio", bg="#f0f2f5").pack(anchor="w")

        # Botões
        tk.Button(self.frame, text="CONFIRMAR GERAÇÃO", bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"),
                  command=self.gerar, height=2, width=20).pack(pady=20)
        
        tk.Button(self.frame, text="Voltar ao Menu", command=self.voltar).pack(pady=5)

    def carregar_dados(self):
        try:
            with open("funcionarios.json", encoding="utf-8") as f:
                self.funcionarios = json.load(f)
            
            # Extrai lista única de unidades e ordena
            # Usa set para remover duplicatas e filter para remover vazios
            unidades_unicas = set(f.get('unidade', 'Geral') for f in self.funcionarios)
            self.unidades = sorted(list(unidades_unicas))

            # Popula o combo de Unidades
            menu = self.combo_unidade["menu"]
            menu.delete(0, "end")
            for u in self.unidades:
                menu.add_command(label=u, command=lambda v=u: self.unidade_var.set(v))

        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo 'funcionarios.json' não encontrado.")

    def filtrar_funcionarios(self, *args):
        """Chamado automaticamente quando a unidade muda"""
        unidade_selecionada = self.unidade_var.get()
        
        # Filtra a lista principal
        funcs_filtrados = [f for f in self.funcionarios if f.get('unidade', 'Geral') == unidade_selecionada]
        funcs_filtrados.sort(key=lambda x: x['nome']) # Ordena por nome

        # Atualiza o combo de funcionários
        menu = self.combo_func["menu"]
        menu.delete(0, "end")
        self.func_var.set("Selecione...")
        
        for f in funcs_filtrados:
            label = f"{f['nome']} ({f.get('matricula', '?')})"
            menu.add_command(label=label, command=lambda v=label: self.func_var.set(v))

    def gerar(self):
        selecao = self.func_var.get()
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

        gerador = GeradorFolhaPonto()

        # BLOCO DE TENTATIVA DE GERAÇÃO (Captura regras de negócio)
        try:
            if self.tipo_var.get() == "impressao":
                import tempfile
                temp_dir = tempfile.gettempdir()
                caminho_pdf = os.path.join(temp_dir, f"Ponto_{func_obj['nome']}_{mes}_{ano}.pdf")
                
                self.parent.config(cursor="wait")
                self.parent.update()
                
                gerador.gerar(func_obj, mes, ano, caminho_pdf)
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
                
                gerador.gerar(func_obj, mes, ano, caminho_pdf)
                messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{caminho_pdf}")

        except ValueError as ve:
            # Captura os erros de regra de negócio (data retroativa, dia 20, etc)
            messagebox.showwarning("Bloqueio de Regra", str(ve))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro crítico na geração: {e}")
        finally:
            self.parent.config(cursor="")