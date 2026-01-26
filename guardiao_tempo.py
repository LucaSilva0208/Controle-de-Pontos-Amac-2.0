import os
import json
import base64
from datetime import datetime, timedelta
import urllib.request

ARQUIVO_SEGURANCA = "security.dat"

def obter_data_rede():
    """Tenta obter a data atual de um servidor confiável (Google)"""
    try:
        # Faz uma requisição leve apenas para pegar o cabeçalho
        with urllib.request.urlopen("http://google.com", timeout=3) as conn:
            data_header = conn.headers['date']
            # Formato do header: 'Fri, 26 Jan 2026 10:00:00 GMT'
            data_online = datetime.strptime(data_header, '%a, %d %b %Y %H:%M:%S %Z')
            return data_online.date()
    except:
        return None

def validar_acesso():
    """
    Retorna (True, Mensagem) se permitido, ou (False, Motivo) se bloqueado.
    """
    hoje_real = obter_data_rede()
    hoje_local = datetime.now().date()
    
    ultimo_acesso = None

    # Tenta ler o último acesso salvo
    if os.path.exists(ARQUIVO_SEGURANCA):
        try:
            with open(ARQUIVO_SEGURANCA, "rb") as f:
                dados_b64 = f.read()
                dados_json = base64.b64decode(dados_b64).decode('utf-8')
                dados = json.loads(dados_json)
                ultimo_acesso = datetime.strptime(dados['last_date'], "%Y-%m-%d").date()
        except:
            # Se arquivo corrompido, reseta ou bloqueia. Vamos resetar se tiver internet.
            pass

    # --- CENÁRIO 1: TEM INTERNET ---
    if hoje_real:
        # Atualiza o arquivo de segurança
        salvar_data_segura(hoje_real)
        
        # Valida se o relógio do Windows não está muito errado (opcional, mas bom aviso)
        diferenca = abs((hoje_real - hoje_local).days)
        if diferenca > 1:
            return True, f"Aviso: Seu relógio local está errado em {diferenca} dias, mas validamos via Internet."
        return True, "Validado Online"

    # --- CENÁRIO 2: SEM INTERNET (OFFLINE) ---
    else:
        if not ultimo_acesso:
            # Primeira vez rodando e sem internet? Permissivo ou Restritivo?
            # Vamos ser permissivos na primeira execução
            salvar_data_segura(hoje_local)
            return True, "Modo Offline (Primeiro Acesso)"

        # VERIFICAÇÃO DE FRAUDE (Retroativo)
        if hoje_local < ultimo_acesso:
            return False, f"ERRO CRÍTICO: Data inconsistente.\nData atual ({hoje_local}) é menor que o último uso ({ultimo_acesso}).\nAjuste o relógio."

        # VERIFICAÇÃO DE LIMITE OFF-LINE (3 dias)
        dias_offline = (hoje_local - ultimo_acesso).days
        if dias_offline > 3:
            return False, f"BLOQUEIO DE SEGURANÇA: Sistema offline por {dias_offline} dias.\nConecte-se à internet para revalidar a licença."

        # Se passou, atualiza a data local como nova referência
        salvar_data_segura(hoje_local)
        return True, f"Modo Offline (Válido por mais {3 - dias_offline} dias)"

def salvar_data_segura(data):
    dados = json.dumps({"last_date": data.strftime("%Y-%m-%d")})
    dados_b64 = base64.b64encode(dados.encode('utf-8'))
    with open(ARQUIVO_SEGURANCA, "wb") as f:
        f.write(dados_b64)

# Teste manual
if __name__ == "__main__":
    status, msg = validar_acesso()
    print(f"Status: {status} | Msg: {msg}")