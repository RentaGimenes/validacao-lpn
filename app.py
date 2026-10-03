import tkinter as tk
from tkinter import messagebox

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Validador de Códigos")
        self.root.geometry("420x350")
        self.root.config(bg="#f0f0f0")

        # Cabeçalho da tela
        titulo = tk.Label(root, text="Leitor de Código de Barras", font=("Arial", 14, "bold"), bg="#f0f0f0")
        titulo.pack(pady=15)

        # Variáveis pra guardar o que for lido em cada input
        self.v1 = tk.StringVar()
        self.v2 = tk.StringVar()
        self.v3 = tk.StringVar()

        # Container dos campos
        box = tk.Frame(root, bg="#f0f0f0")
        box.pack(pady=5)

        # Campo 1
        tk.Label(box, text="Primeiro Código:", font=("Arial", 11), bg="#f0f0f0").pack(anchor="w", pady=2)
        self.e1 = tk.Entry(box, textvariable=self.v1, font=("Arial", 14), width=25)
        self.e1.pack(pady=5)
        self.e1.bind("<Return>", lambda e: self.pula_para_dois())

        # Campo 2
        tk.Label(box, text="Segundo Código:", font=("Arial", 11), bg="#f0f0f0").pack(anchor="w", pady=2)
        self.e2 = tk.Entry(box, textvariable=self.v2, font=("Arial", 14), width=25)
        self.e2.pack(pady=5)
        self.e2.bind("<Return>", lambda e: self.pula_para_tres())

        # Campo 3
        tk.Label(box, text="Terceiro Código:", font=("Arial", 11), bg="#f0f0f0").pack(anchor="w", pady=2)
        self.e3 = tk.Entry(box, textvariable=self.v3, font=("Arial", 14), width=25)
        self.e3.pack(pady=5)
        self.e3.bind("<Return>", lambda e: self.processa_validacao())

        # Texto embaixo pra ver o status atual
        self.status = tk.Label(root, text="Bipe o primeiro código...", font=("Arial", 10, "italic"), fg="gray", bg="#f0f0f0")
        self.status.pack(pady=15)

        # Já joga o cursor direto no primeiro input
        self.e1.focus_set()

    def pula_para_dois(self):
        # Só avança se tiver algo digitado no primeiro
        if self.v1.get().strip():
            self.e2.focus_set()
            self.status.config(text="Aguardando o segundo...", fg="blue")
        else:
            messagebox.showwarning("Opa!", "Preencha o primeiro campo antes.")

    def pula_para_tres(self):
        # Só avança se tiver algo no segundo
        if self.v2.get().strip():
            self.e3.focus_set()
            self.status.config(text="Aguardando o terceiro...", fg="blue")
        else:
            messagebox.showwarning("Opa!", "Preencha o segundo campo antes.")

    def processa_validacao(self):
        # Pega os valores dos três campos
        c1 = self.v1.get().strip()
        c2 = self.v2.get().strip()
        c3 = self.v3.get().strip()

        if not c3:
            messagebox.showwarning("Opa!", "Faltou o terceiro código!")
            return

        # TODO: Colocar aqui a lógica de validação ou consulta na planilha depois
        print(f"Lote lido -> {c1} | {c2} | {c3}")
        
        self.status.config(text="Validado com sucesso!", fg="green")

        # Limpa tudo pra reiniciar o ciclo do zero
        self.v1.set("")
        self.v2.set("")
        self.v3.set("")

        # Devolve o foco pro começo da fila
        self.e1.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
