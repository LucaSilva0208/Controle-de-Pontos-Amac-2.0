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

        self.frame = tk.Frame(parent, bg="#f0f2f5") # Cor mais suave
        self.frame.pack(fill="both", expand=True)

        self.funcionarios = []
        self.criar_layout()
        self.carregar_funcionarios()

    def criar_layout(self):
        tk.Label(self.frame, text="Gerar Folha Individual",
                 font=("Segoe UI", 20, "bold"), bg="#f0f2f5").pack(pady=20)

        container = tk.Frame(self.frame, bg="#f0f2f5")
        container.pack(pady=10)

        # Seleção de funcionário
        tk.Label(container, text="Selecione o Funcionário:", bg="#f0f2f5").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.func_var = tk.StringVar(self.frame)
        self.combo = tk.OptionMenu(container, self.func_var, "")
        self.combo.config(width=30)
        self.combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Mês e Ano
        tk.Label(container, text="Mês (1-12):", bg="#f0f2f5").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.mes_var = tk.IntVar(value=datetime.datetime.now().month)
        tk.Entry(container, textvariable=self.mes_var, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(container, text="Ano:", bg="#f0f2f5").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.ano_var = tk.IntVar(value=datetime.datetime.now().year)
        tk.Entry(container, textvariable=self.ano_var, width=10).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Tipo de geração
        tk.Label(container, text="Ação:", bg="#f0f2f5").grid(row=3, column=0, sticky="ne", padx=5, pady=5)
        self.tipo_var = tk.StringVar(value="impressao")
        frame_radio = tk.Frame(container, bg="#f0f2f5")
        frame_radio.grid(row=3, column=1, sticky="w")
        
        tk.Radiobutton(frame_radio, text="Imprimir (Abrir PDF)", variable=self.tipo_var, value="impressao", bg="#f0f2f5").pack(anchor="w")
        tk.Radiobutton(frame_radio, text="Salvar PDF", variable=self.tipo_var, value="envio", bg="#f0f2f5").pack(anchor="w")

        # Botões
        tk.Button(self.frame, text="CONFIRMAR GERAÇÃO", bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"),
                  command=self.gerar, height=2, width=20).pack(pady=20)
        
        tk.Button(self.frame, text="Voltar ao Menu", command=self.voltar).pack(pady=5)

    def carregar_funcionarios(self):
        try:
            with open("funcionarios.json", encoding="utf-8") as f:
                self.funcionarios = json.load(f)
            
            menu = self.combo["menu"]
            menu.delete(0, "end")
            self.func_var.set("Selecione...")
            
            for f in self.funcionarios:
                label = f"{f['nome']} ({f.get('matricula', '?')})"
                menu.add_command(label=label, command=lambda v=label: self.func_var.set(v))
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo 'funcionarios.json' não encontrado.")

    def gerar(self):
        selecao = self.func_var.get()
        if not selecao or selecao == "Selecione...":
            messagebox.showwarning("Atenção", "Selecione um funcionário.")
            return

        # Recuperar objeto funcionário pelo nome/string do combo
        # Estratégia simples: match pelo nome que está na string
        nome_selecionado = selecao.split(" (")[0] # Pega só o nome antes da matrícula
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

        gerador = GeradorFolhaPonto() # Instancia aqui para pegar erro de path se houver

        if self.tipo_var.get() == "impressao":
            # Gera em pasta temporária do sistema
            import tempfile
            temp_dir = tempfile.gettempdir()
            caminho_pdf = os.path.join(temp_dir, f"Ponto_{func_obj['nome']}_{mes}_{ano}.pdf")
            
            self.parent.config(cursor="wait") # Muda cursor
            self.parent.update()
            
            try:
                gerador.gerar(func_obj, mes, ano, caminho_pdf)
                os.startfile(caminho_pdf) # Abre com o visualizador padrão
            except Exception as e:
                messagebox.showerror("Erro", f"Erro na geração: {e}")
            finally:
                self.parent.config(cursor="")
                
        else: # envio/salvar
            caminho_pdf = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                initialfile=f"Ponto_{func_obj['nome']}_{mes}_{ano}.pdf",
                title="Salvar Folha de Ponto"
            )
            if not caminho_pdf:
                return
            
            self.parent.config(cursor="wait")
            self.parent.update()
            try:
                gerador.gerar(func_obj, mes, ano, caminho_pdf)
                messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{caminho_pdf}")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar: {e}")
            finally:
                self.parent.config(cursor="")