import tkinter as tk
from tela_login import TelaLogin
import base64

if __name__ == "__main__":
    
    _sig = b'Q29kZSBieSBbU2V1IE5vbWVd' 
    print(f"System Init :: {base64.b64decode(_sig).decode('utf-8')}")

    root = tk.Tk()
    TelaLogin(root)
    root.mainloop()
