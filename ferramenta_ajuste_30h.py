import tkinter as tk
from tkinter import messagebox
from repositorio_dados import RepositorioDados

class FerramentaAjuste30h:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ajuste de Carga Horária (30h)")
        self.repo = RepositorioDados()
        self.vars = []
        
        tk.Label(self.root, text="Selecione os funcionários com carga de 30h:", 
                 font=("Segoe UI", 12, "bold"), bg="#f0f2f5").pack(fill="x", pady=10)
        
        frame_list = tk.Frame(self.root)
        frame_list.pack(fill="both", expand=True, padx=10)
        
        canvas = tk.Canvas(frame_list, bg="white")
        scroll = tk.Scrollbar(frame_list, command=canvas.yview)
        self.scrollable = tk.Frame(canvas, bg="white")
        
        self.scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        self.carregar()
        
        tk.Button(self.root, text="💾 SALVAR ALTERAÇÕES NO EXCEL", command=self.salvar, 
                  bg="#22c55e", fg="white", font=("Segoe UI", 10, "bold"), pady=10).pack(pady=10, fill="x", padx=20)
        
        self.root.geometry("500x600")
        self.root.mainloop()

    def carregar(self):
        funcs = self.repo.listar_todos_funcionarios()
        funcs.sort(key=lambda x: x['nome'])
        
        for f in funcs:
            is_30h = f.get('carga_horaria') == '30h'
            var = tk.BooleanVar(value=is_30h)
            
            chk = tk.Checkbutton(self.scrollable, text=f"{f['nome']} ({f['matricula']})", 
                                 variable=var, anchor="w", bg="white", font=("Segoe UI", 10))
            chk.pack(fill="x", padx=5, pady=2)
            self.vars.append((f, var))

    def salvar(self):
        count = 0
        for f, var in self.vars:
            nova_carga = "30h" if var.get() else "40h"
            # Só atualiza se mudou
            if f.get('carga_horaria') != nova_carga:
                self.repo.editar_funcionario(
                    f['matricula'], f['nome'], f['matricula'], 
                    f['cargo'], f.get('escala', 'NORMAL'), nova_carga
                )
                count += 1
        messagebox.showinfo("Sucesso", f"{count} funcionários atualizados para a nova carga horária!")

if __name__ == "__main__":
    FerramentaAjuste30h()