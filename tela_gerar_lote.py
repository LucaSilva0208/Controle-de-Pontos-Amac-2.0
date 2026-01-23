import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import zipfile
import tempfile
import datetime
from gerador_folha import GeradorFolhaPonto

class TelaGerarLote:
    def __init__(self, parent, voltar_callback):
        self.parent = parent
        self.voltar = voltar_callback

        self.frame = tk.Frame(parent, bg="#e5e7eb")
        self.frame.pack(fill="both", expand=True)

        self.vars = [] 
        self.funcionarios = []
        self.criar_layout()
        self.carregar_funcionarios()

    def criar_layout(self):
        # Cabeçalho
        header = tk.Frame(self.frame, bg="#e5e7eb")
        header.pack(fill="x", pady=10)
        tk.Label(header, text="Gerar Folhas em Lote", font=("Segoe UI", 18, "bold"), bg="#e5e7eb").pack()

        # Filtro
        frame_filtro = tk.Frame(self.frame, bg="#e5e7eb")
        frame_filtro.pack(fill="x", padx=20)
        tk.Label(frame_filtro, text="Filtrar:", bg="#e5e7eb").pack(side="left")
        self.busca = tk.StringVar()
        self.busca.trace_add("write", self.filtrar)
        tk.Entry(frame_filtro, textvariable=self.busca).pack(side="left", fill="x", expand=True, padx=5)

        # Área de Lista com Scroll (Importante para muitos funcionários)
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

        # Botões de Ação
        frame_botoes = tk.Frame(self.frame, bg="#e5e7eb")
        frame_botoes.pack(fill="x", pady=20, padx=20)

        tk.Button(frame_botoes, text="Gerar para Impressão (Pasta)", command=lambda: self.gerar("impressao"), 
                  bg="#2196F3", fg="white", width=25).pack(side="left", padx=5)
        
        tk.Button(frame_botoes, text="Gerar para Envio (ZIP)", command=lambda: self.gerar("envio"), 
                  bg="#FF9800", fg="white", width=25).pack(side="left", padx=5)
        
        tk.Button(frame_botoes, text="Voltar", command=self.voltar).pack(side="right")

    def carregar_funcionarios(self):
        try:
            with open("funcionarios.json", encoding="utf-8") as f:
                self.funcionarios = json.load(f)
            
            # Ordena por nome
            self.funcionarios.sort(key=lambda x: x['nome'])

            # Inicializa Vars
            for f in self.funcionarios:
                self.vars.append((f, tk.BooleanVar(value=True)))

            self.atualizar_lista(self.funcionarios)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler funcionarios.json: {e}")

    def atualizar_lista(self, lista_filtrada):
        # Limpa widgets antigos
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Botões de selecionar tudo/nenhum
        frame_tools = tk.Frame(self.scrollable_frame, bg="white")
        frame_tools.pack(fill="x", pady=2)
        tk.Button(frame_tools, text="Marcar Todos", command=lambda: self.toggle_all(True), font=("Arial", 8)).pack(side="left")
        tk.Button(frame_tools, text="Desmarcar Todos", command=lambda: self.toggle_all(False), font=("Arial", 8)).pack(side="left")

        for f in lista_filtrada:
            # Encontra a var correspondente na lista global
            par = next((p for p in self.vars if p[0]["matricula"] == f["matricula"]), None)
            if par:
                func, var = par
                cb = tk.Checkbutton(self.scrollable_frame, text=f"{func['nome']} ({func['matricula']})", 
                                    variable=var, bg="white", anchor="w")
                cb.pack(fill="x", padx=5)

    def toggle_all(self, state):
        termo = self.busca.get().lower()
        # Afeta apenas os visíveis no filtro atual? Ou todos? Geralmente os visíveis.
        for f, var in self.vars:
             if termo in f["nome"].lower() or termo in f["matricula"]:
                 var.set(state)

    def filtrar(self, *args):
        termo = self.busca.get().lower()
        filtrados = [f for f, _ in self.vars if termo in f["nome"].lower() or termo in f["matricula"]]
        self.atualizar_lista(filtrados)

    def gerar(self, tipo):
        selecionados = [f for f, v in self.vars if v.get()]
        if not selecionados:
            messagebox.showwarning("Atenção", "Nenhum funcionário selecionado.")
            return

        mes = datetime.datetime.today().month
        ano = datetime.datetime.today().year
        
        try:
            gerador = GeradorFolhaPonto()
        except FileNotFoundError:
            messagebox.showerror("Erro", "Modelo Word não encontrado.")
            return

        self.parent.config(cursor="wait")
        self.parent.update()

        try:
            if tipo == "impressao":
                pasta_destino = filedialog.askdirectory(title="Onde salvar os PDFs?")
                if not pasta_destino: return

                for f in selecionados:
                    nome_arq = f"{f['nome'].replace(' ', '_')}_{mes}_{ano}.pdf"
                    caminho = os.path.join(pasta_destino, nome_arq)
                    gerador.gerar(f, mes, ano, caminho)
                
                messagebox.showinfo("Sucesso", f"{len(selecionados)} arquivos gerados em:\n{pasta_destino}")

            else: # ZIP
                caminho_zip = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP", "*.zip")], title="Salvar Arquivo ZIP")
                if not caminho_zip: return

                # Usa diretório temporário seguro para gerar os PDFs antes de zipar
                with tempfile.TemporaryDirectory() as temp_dir:
                    arquivos_pdf = []
                    for f in selecionados:
                        nome_arq = f"{f['nome'].replace(' ', '_')}_{mes}_{ano}.pdf"
                        caminho_temp = os.path.join(temp_dir, nome_arq)
                        gerador.gerar(f, mes, ano, caminho_temp)
                        arquivos_pdf.append(nome_arq) # Guarda só o nome para o zip

                    # Cria o ZIP final
                    with zipfile.ZipFile(caminho_zip, 'w') as zipf:
                        for arq in arquivos_pdf:
                            zipf.write(os.path.join(temp_dir, arq), arcname=arq)
                
                messagebox.showinfo("Sucesso", f"ZIP gerado com sucesso:\n{caminho_zip}")

        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Falha na geração em lote: {e}")
        finally:
            self.parent.config(cursor="")