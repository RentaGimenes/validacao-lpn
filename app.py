import tkinter as tk
from tkinter import messagebox

class AppValidacaoCodigos:
    def __init__(self, root):
        self.root = root
        self.root.title("Validação de Códigos de Barras")
        self.root.geometry("420x350")
        self.root.config(bg="#f0f0f0")

        # Título do projeto // Leitura e validação dos lotes
        titulo = tk.Label(root, text="Leitor e Validador de Lote", font=("Arial", 14, "bold"), bg="#f0f0f0")
        titulo.pack(pady=15)

        # Variáveis para os campos
        self.var1 = tk.StringVar()
        self.var2 = tk.StringVar()
        self.var3 = tk.StringVar()

        # Frame para organizar os campos
        frame_campos = tk.Frame(root, bg="#f0f0f0")
        frame_campos.pack(pady=5)

        # --- CAMPO 1 ---// primeiro código de barras // o que vai para a planilha
        tk.Label(frame_campos, text="1º Código:", font=("Arial", 11), bg="#f0f0f0").pack(anchor="w", pady=2)
        self.entry1 = tk.Entry(frame_campos, textvariable=self.var1, font=("Arial", 14), width=25)
        self.entry1.pack(pady=5)
        # Vincula a tecla Enter (Return) para ir ao campo 2
        self.entry1.bind("<Return>", lambda event: self.focar_campo2())

        # --- CAMPO 2 ---// seg. aqui confirma o material e o lote
        tk.Label(frame_campos, text="2º Código:", font=("Arial", 11), bg="#f0f0f0").pack(anchor="w", pady=2)
        self.entry2 = tk.Entry(frame_campos, textvariable=self.var2, font=("Arial", 14), width=25)
        self.entry2.pack(pady=5)
        # alteração para ir para o proximo automaticamente
        self.entry2.bind("<Return>", lambda event: self.focar_campo3())

        # --- CAMPO 3 ---// ter. valida a dun e as datas de criação e validade
        tk.Label(frame_campos, text="3º Código:", font=("Arial", 11), bg="#f0f0f0").pack(anchor="w", pady=2)
        self.entry3 = tk.Entry(frame_campos, textvariable=self.var3, font=("Arial", 14), width=25)
        self.entry3.pack(pady=5)
        # alteração para validar direto após o 3 bipe
        self.entry3.bind("<Return>", lambda event: self.validar_e_limpar())

        # status / Feedback visual 
        self.lbl_status = tk.Label(root, text="Aguardando leitura do 1º código...", font=("Arial", 10, "italic"), fg="gray", bg="#f0f0f0")
        self.lbl_status.pack(pady=15)

        # configurar o foco inicial no primeiro campo ao abrir o programa
        self.entry1.focus_set()

    def focar_campo2(self):
        if self.var1.get().strip():
            self.entry2.focus_set()
            self.lbl_status.config(text="Aguardando leitura do 2º código...", fg="blue")
        else:
            messagebox.showwarning("Atenção", "O primeiro campo está vazio!")

    def focar_campo3(self):
        if self.var2.get().strip():
            self.entry3.focus_set()
            self.lbl_status.config(text="Aguardando leitura do 3º código...", fg="blue")
        else:
            messagebox.showwarning("Atenção", "O segundo campo está vazio!")

    def validar_e_limpar(self):
        c1 = self.var1.get().strip()
        c2 = self.var2.get().strip()
        c3 = self.var3.get().strip()

        if not c3:
            messagebox.showwarning("Atenção", "O terceiro campo está vazio!")
            return

        # ==========================================
        # iniciando a logica de validação // bater com as infos da planilha
        # ==========================================
        print(f"Validando lote -> C1: {c1} | C2: {c2} | C3: {c3}")
        
        # simulando uma validação bem-sucedida:
        
        # atualiza o status informando quando da certo
        self.lbl_status.config(text=f"Último lote validado com sucesso!", fg="green")

        # LIMPA OS CAMPOS PARA O PRÓXIMO CICLO // EXTREMAMANTE FUNCIONAL 
        self.var1.set("")
        self.var2.set("")
        self.var3.set("")

        # devolve o foco automaticamente para o primeiro campo
        self.entry1.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppValidacaoCodigos(root)
    root.mainloop()
