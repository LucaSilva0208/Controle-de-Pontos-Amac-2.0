import json
import random

nomes = [
    "João Silva", "Maria Oliveira", "Carlos Santos", "Ana Costa",
    "Paulo Mendes", "Fernanda Rocha", "Lucas Pereira", "Juliana Alves",
    "Rafael Lima", "Patrícia Nogueira", "Bruno Ribeiro", "Camila Teixeira"
]

cargos = ["Analista", "Assistente", "Gerente", "Coordenador", "Auxiliar", "Supervisor"]
status = ["ativo", "férias", "afastado"]


def gerar_funcionarios(qtd=25, arquivo="funcionarios.json"):
    funcionarios = []
    used_matriculas = set()

    for i in range(1, qtd + 1):
        # Garante matrícula única
        matricula = f"{1000 + i}"
        while matricula in used_matriculas:
            matricula = str(random.randint(1000, 9999))
        used_matriculas.add(matricula)

        func = {
            "nome": random.choice(nomes),
            "cargo": random.choice(cargos),
            "matricula": matricula,
            "status": random.choice(status)
        }

        funcionarios.append(func)

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(funcionarios, f, indent=4, ensure_ascii=False)

    print(f"✔ {arquivo} gerado com sucesso com {qtd} funcionários!")


if __name__ == "__main__":
    gerar_funcionarios()
