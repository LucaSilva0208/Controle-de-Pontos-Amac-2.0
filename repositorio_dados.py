import json
import os

# Arquivos
ARQUIVO_USUARIOS = "usuarios_sistema.json"
ARQUIVO_FUNCIONARIOS = "funcionarios.json"

class RepositorioDados:
    def __init__(self):
        # Garante que o arquivo de usuários existe com o admin padrão
        if not os.path.exists(ARQUIVO_USUARIOS):
            dados_iniciais = {
                "admin": {
                    "senha": "1234",
                    "perfil": "admin",
                    "unidade": "Sede Administrativa"
                }
            }
            with open(ARQUIVO_USUARIOS, 'w', encoding='utf-8') as f:
                json.dump(dados_iniciais, f, indent=4)

    # --- MÉTODOS DE USUÁRIOS (LOGIN) ---
    
    def buscar_usuario_login(self, login):
        """Lê o usuário do JSON"""
        try:
            with open(ARQUIVO_USUARIOS, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                usuario = dados.get(login)
                if usuario:
                    usuario['login'] = login # Adiciona o login ao objeto
                    return usuario
        except Exception as e:
            print(f"Erro leitura: {e}")
        return None

    def salvar_novo_usuario(self, login, senha, perfil, unidade):
        """Escreve um novo usuário no JSON"""
        try:
            # 1. Lê tudo que já existe
            with open(ARQUIVO_USUARIOS, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            # 2. Verifica se já existe
            if login in dados:
                return False, "Usuário já existe."

            # 3. Adiciona o novo
            dados[login] = {
                "senha": senha,
                "perfil": perfil,
                "unidade": unidade
            }

            # 4. Salva de volta no arquivo
            with open(ARQUIVO_USUARIOS, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4)
            
            return True, "Usuário criado com sucesso!"
        except Exception as e:
            return False, f"Erro ao salvar: {e}"

    def excluir_usuario(self, login):
        """Remove usuário do JSON"""
        if login == "admin": 
            return False, "Não pode excluir o Admin."
            
        try:
            with open(ARQUIVO_USUARIOS, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            if login in dados:
                del dados[login]
                
                with open(ARQUIVO_USUARIOS, 'w', encoding='utf-8') as f:
                    json.dump(dados, f, indent=4)
                return True, "Usuário removido."
            else:
                return False, "Usuário não encontrado."
        except Exception as e:
            return False, f"Erro: {e}"

    def listar_usuarios(self):
        """Retorna lista para a tela de gestão"""
        try:
            with open(ARQUIVO_USUARIOS, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                lista = []
                for login, infos in dados.items():
                    # Formata para o TreeView
                    lista.append((login, login, infos['unidade'], infos['perfil']))
                return lista
        except:
            return []

    # --- MÉTODOS DE FUNCIONÁRIOS (FOLHA) ---
    # (Mantém igual ao anterior)
    def listar_todos_funcionarios(self):
        if not os.path.exists(ARQUIVO_FUNCIONARIOS): return []
        with open(ARQUIVO_FUNCIONARIOS, 'r', encoding='utf-8') as f:
            return json.load(f)

    def buscar_funcionarios_por_unidade(self, unidade):
        todos = self.listar_todos_funcionarios()
        if unidade == "Todas": return todos
        return [f for f in todos if f.get('unidade') == unidade]

    def buscar_unidades(self):
        todos = self.listar_todos_funcionarios()
        unidades = list(set(f.get('unidade', 'Indefinido') for f in todos))
        unidades.sort()
        return unidades