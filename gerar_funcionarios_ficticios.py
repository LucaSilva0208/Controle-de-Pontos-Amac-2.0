import json
import random

nomes = [
    "João Silva", "Maria Oliveira", "Carlos Santos", "Ana Costa",
    "Paulo Mendes", "Fernanda Rocha", "Lucas Pereira", "Juliana Alves",
    "Rafael Lima", "Patrícia Nogueira", "Bruno Ribeiro", "Camila Teixeira"
]

cargos = ["Analista", "Assistente", "Gerente", "Coordenador", "Auxiliar", "Supervisor"]
status = ["ativo", "férias", "afastado"]

funcionarios = []

for i in range(1, 26):
    nome = random.choice(nomes)
    func = {
        "nome": nome,
        "cargo": random.choice(cargos),
        "matricula": f"{1000+i}",
        "status": random.choice(status)
    }
    funcionarios.append(func)

with open("funcionarios.json", "w", encoding="utf-8") as f:
    json.dump(funcionarios, f, indent=4, ensure_ascii=False)

print("✔ funcionarios.json gerado com sucesso!")
