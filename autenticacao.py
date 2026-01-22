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
        print("DEBUG → Tentando login com:")
        print("Usuário digitado:", repr(usuario))
        print("Senha digitada:", repr(senha))
        print("Arquivo usado:", os.path.abspath(self.arquivo))

        with open(self.arquivo, "r", encoding="utf-8") as f:
            usuarios = json.load(f)

        print("DEBUG → Usuários carregados:", usuarios)

        if usuario in usuarios and usuarios[usuario]["senha"] == senha:
            print("DEBUG → LOGIN OK")
            return usuarios[usuario]["perfil"]

        print("DEBUG → LOGIN FALHOU")
        return None
