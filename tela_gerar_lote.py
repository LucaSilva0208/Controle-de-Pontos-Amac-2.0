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
        tk.Label(header, text="Gerar Folhas em Lote (Por Unidade)", font=("Segoe UI", 18, "bold"), bg="#e5e7eb").pack()

        # Filtro
        frame_filtro = tk.Frame(self.frame, bg="#e5e7eb")
        frame_filtro.pack(fill="x", padx=20)
        tk.Label(frame_filtro, text="Filtrar (Nome ou Unidade):", bg="#e5e7eb").pack(side="left")
        self.busca = tk.StringVar()
        self.busca.trace("w", self.filtrar)
        tk.Entry(frame_filtro, textvariable=self.busca).pack(side="left", fill="x", expand=True, padx=5)

        # Área de Lista com Scroll
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

        # Botões de Seleção
        frame_sel = tk.Frame(self.frame, bg="#e5e7eb")
        frame_sel.pack(fill="x", padx=20)
        tk.Button(frame_sel, text="Marcar Ativos", command=lambda: self.toggle_ativos(True), font=("Arial", 8)).pack(side="left", padx=2)
        tk.Button(frame_sel, text="Desmarcar Todos", command=lambda: self.toggle_all(False), font=("Arial", 8)).pack(side="left", padx=2)

        tk.Button(frame_botoes, text="Gerar Impressão (Pastas)", command=lambda: self.gerar("impressao"), 
                  bg="#2196F3", fg="white", width=20, height=2).pack(side="left", padx=5)
        
        tk.Button(frame_botoes, text="Gerar ZIP (Organizado)", command=lambda: self.gerar("envio"), 
                  bg="#4CAF50", fg="white", width=30, height=2).pack(side="left", padx=5)
        
        tk.Button(frame_botoes, text="Voltar", command=self.voltar).pack(side="right")

    def carregar_funcionarios(self):
        try:
            with open("funcionarios.json", encoding="utf-8") as f:
                self.funcionarios = json.load(f)
            
            # Ordena por Unidade -> Status (Ativos primeiro) -> Nome
            self.funcionarios.sort(key=lambda x: (x.get('unidade', 'Geral'), x.get('status', 'Ativo'), x['nome']))

            # Inicializa Vars
            for f in self.funcionarios:
                status = f.get('status', 'Ativo')
                # Só marca por padrão se NÃO for desligado
                is_ativo = status != "Desligado"
                self.vars.append((f, tk.BooleanVar(value=is_ativo)))

            self.atualizar_lista(self.funcionarios)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler funcionarios.json: {e}")

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
                
                # Formatação Visual do Item
                cor_texto = "black"
                texto_extra = ""
                
                if status == "Desligado":
                    cor_texto = "red"
                    texto_extra = " (DESLIGADO)"
                elif status == "Férias":
                    cor_texto = "#FFA500" # Laranja
                    texto_extra = " (FÉRIAS)"
                elif status == "Afastado":
                    cor_texto = "purple"
                    texto_extra = " (AFASTADO)"

                texto_display = f"{func['nome']}{texto_extra}"
                
                cb = tk.Checkbutton(self.scrollable_frame, text=texto_display, 
                                    variable=var, bg="white", fg=cor_texto, anchor="w")
                cb.pack(fill="x", padx=10)

    def toggle_all(self, state):
        termo = self.busca.get().lower()
        for f, var in self.vars:
             if self.match_filtro(f, termo):
                 var.set(state)

    def toggle_ativos(self, state):
        """Marca apenas quem não está desligado"""
        termo = self.busca.get().lower()
        for f, var in self.vars:
             if self.match_filtro(f, termo):
                 if f.get('status') != "Desligado":
                    var.set(state)

    def match_filtro(self, f, termo):
        unidade = f.get('unidade', '').lower()
        return termo in f["nome"].lower() or termo in f["matricula"] or termo in unidade

    def filtrar(self, *args):
        termo = self.busca.get().lower()
        filtrados = [f for f, _ in self.vars if self.match_filtro(f, termo)]
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
            # Valida regra de negócio global (se data inválida, para tudo aqui)
            gerador.validar_regras_negocio(mes, ano) 
        except ValueError as ve:
            messagebox.showwarning("Bloqueio de Regra", str(ve))
            return
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivos de modelo não encontrados.")
            return

        self.parent.config(cursor="wait")
        self.parent.update()

        try:
            if tipo == "impressao":
                pasta_raiz = filedialog.askdirectory(title="Onde salvar as pastas?")
                if not pasta_raiz: 
                    self.parent.config(cursor="")
                    return

                count = 0
                erros = []
                for f in selecionados:
                    unidade = f.get('unidade', 'Geral').strip()
                    pasta_unidade = os.path.join(pasta_raiz, unidade)
                    os.makedirs(pasta_unidade, exist_ok=True)

                    nome_arq = f"{f['nome'].replace(' ', '_')}_{mes}_{ano}.pdf"
                    caminho = os.path.join(pasta_unidade, nome_arq)
                    
                    try:
                        gerador.gerar(f, mes, ano, caminho)
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
                    for f in selecionados:
                        unidade = f.get('unidade', 'Geral').strip()
                        pasta_u_temp = os.path.join(temp_dir, unidade)
                        os.makedirs(pasta_u_temp, exist_ok=True)

                        nome_arq = f"{f['nome'].replace(' ', '_')}.pdf"
                        caminho_abs = os.path.join(pasta_u_temp, nome_arq)
                        
                        try:
                            gerador.gerar(f, mes, ano, caminho_abs)
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
            self.parent.config(cursor="")