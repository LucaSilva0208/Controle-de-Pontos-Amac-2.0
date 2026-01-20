import json
import os

class Autenticacao:
    def __init__(self, arquivo="usuarios.json"):
        self.arquivo = arquivo
        self.criar_admin_padrao()

    def criar_admin_padrao(self):
        if not os.path.exists(self.arquivo):
            with open(self.arquivo, "w", encoding="utf-8") as f:
                json.dump({
                    "admin": {
                        "senha": "1234",
                        "perfil": "admin"
                    }
                }, f, indent=4, ensure_ascii=False)

    def validar(self, usuario, senha):
        with open(self.arquivo, "r", encoding="utf-8") as f:
            usuarios = json.load(f)

        if usuario in usuarios and usuarios[usuario]["senha"] == senha:
            return usuarios[usuario]["perfil"]
        return None
