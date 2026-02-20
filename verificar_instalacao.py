import sys
import os

print("="*60)
print("DIAGNÓSTICO DE AMBIENTE PYTHON")
print("="*60)

print(f"Executável Python em uso:\n{sys.executable}")
print(f"\nVersão:\n{sys.version}")
print("-" * 60)

bibliotecas = ["openpyxl", "docx", "docx2pdf", "holidays"]

print("Verificando bibliotecas necessárias:\n")

for lib in bibliotecas:
    try:
        __import__(lib)
        print(f"[OK]     {lib} está instalada.")
    except ImportError:
        print(f"[FALHA]  {lib} NÃO foi encontrada.")

print("-" * 60)
print("DICA: Se as bibliotecas aparecem como [FALHA], você instalou")
print("em um Python diferente do que está usando agora.")
print("")
print("Para corrigir, tente rodar no terminal:")
print(f"\"{sys.executable}\" -m pip install -r requirements.txt")
print("="*60)

if os.name == 'nt':
    input("Pressione ENTER para fechar...")