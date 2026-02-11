import json
import os
try:
    import openpyxl
except ImportError:
    print("ERRO: Instale a biblioteca openpyxl: pip install openpyxl")
    exit()

ARQUIVO_ANTIGO = "funcionarios.json"
ARQUIVO_NOVO_EXCEL = "funcionarios_sede.xlsx"
ARQUIVO_NOVO_AFASTAMENTOS = "afastamentos.json"

def migrar():
    if not os.path.exists(ARQUIVO_ANTIGO):
        print(f"Arquivo antigo '{ARQUIVO_ANTIGO}' não encontrado. Nada a migrar.")
        return

    print("Lendo dados antigos...")
    with open(ARQUIVO_ANTIGO, 'r', encoding='utf-8') as f:
        dados_antigos = json.load(f)

    # --- 1. MIGRAR PARA EXCEL ---
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Funcionarios"
    # Cabeçalho
    ws.append(["Nome Completo", "Matrícula", "Cargo", "Unidade", "Escala"])

    # --- 2. PREPARAR AFASTAMENTOS ---
    lista_ferias = []

    count = 0
    for func in dados_antigos:
        nome = func.get("nome", "")
        matricula = func.get("matricula", "")
        cargo = func.get("cargo", "")
        unidade = func.get("unidade", "Sede")
        
        # Define escala padrão (pode ser ajustado manualmente no Excel depois)
        escala = "NORMAL" 

        # Adiciona linha no Excel
        ws.append([nome, matricula, cargo, unidade, escala])
        count += 1

        # Migra férias se houver
        ferias_antigas = func.get("ferias", [])
        for f in ferias_antigas:
            lista_ferias.append({
                "matricula": matricula,
                "inicio": f["inicio"],
                "fim": f["fim"]
            })

    wb.save(ARQUIVO_NOVO_EXCEL)
    print(f"Sucesso! {count} funcionários exportados para '{ARQUIVO_NOVO_EXCEL}'.")

    # --- 3. SALVAR AFASTAMENTOS ---
    dados_afast = {
        "ferias": lista_ferias,
        "recessos": []
    }
    with open(ARQUIVO_NOVO_AFASTAMENTOS, 'w', encoding='utf-8') as f:
        json.dump(dados_afast, f, indent=4)
    print(f"Sucesso! {len(lista_ferias)} registros de férias migrados para '{ARQUIVO_NOVO_AFASTAMENTOS}'.")

if __name__ == "__main__":
    migrar()