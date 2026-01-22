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
