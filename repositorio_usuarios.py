import json

class RepositorioUsuarios:
    def __init__(self, arquivo="usuarios.json"):
        self.arquivo = arquivo

    def carregar(self):
        try:
            with open(self.arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def salvar(self, dados):
        with open(self.arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

    def existe_usuario(self, username):
        dados = self.carregar()
        return username in dados

    def buscar_todos(self):
        return self.carregar()

    def buscar_por_login(self, login):
        dados = self.carregar()
        return dados.get(login)

    def salvar_usuario(self, login, senha, perfil, unidade):
        dados = self.carregar()
        dados[login] = {
            "senha": senha,
            "perfil": perfil,
            "unidade": unidade
        }
        self.salvar(dados)

    def excluir_usuario(self, login):
        dados = self.carregar()
        if login in dados:
            del dados[login]
            self.salvar(dados)
            return True
        return False
