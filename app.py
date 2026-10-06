import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class BarcodeQualityControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle de Qualidade - Leitura de Etiquetas")
        self.root.geometry("700x500")
        self.root.config(bg="#f0f0f0")

        # Lista para armazenar histórico local de leituras (simulando validação)
        self.historico_leituras = set()

        self.criar_widgets()

    def criar_widgets(self):
        # Título do Aplicativo
        titulo_label = tk.Label(
            self.root, 
            text="Sistema de Validação e Controle de Qualidade", 
            font=("Arial", 16, "bold"), 
            bg="#f0f0f0", 
            fg="#333333"
        )
        titulo_label.pack(pady=15)

        # Frame de Entrada
        input_frame = tk.LabelFrame(
            self.root, 
            text=" Leitura do Código de Barras ", 
            font=("Arial", 11, "bold"), 
            bg="#f0f0f0", 
            padx=15, 
            pady=15
        )
        input_frame.pack(fill="x", padx=20, pady=10)

        self.instrucao_label = tk.Label(
            input_frame, 
            text="Aguardando leitura do código de barras...", 
            font=("Arial", 10), 
            bg="#f0f0f0", 
            fg="#666666"
        )
        self.instrucao_label.pack(anchor="w", pady=5)

        # Campo de entrada (onde a pistola de código de barras insere o texto e envia <Return>)
        self.entry_barcode = tk.Entry(input_frame, font=("Arial", 14), width=40)
        self.entry_barcode.pack(fill="x", pady=5)
        self.entry_barcode.bind("<Return>", self.processar_codigo)
        # Mantém o cursor focado permanentemente neste campo
        self.entry_barcode.focus()

        # Frame de Status / Log
        log_frame = tk.LabelFrame(
            self.root, 
            text=" Histórico de Validações ", 
            font=("Arial", 11, "bold"), 
            bg="#f0f0f0", 
            padx=15, 
            pady=15
        )
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Caixa de Texto com Barra de Rolagem
        self.txt_log = tk.Text(log_frame, font=("Courier", 10), state="disabled", bg="#ffffff")
        scrollbar = tk.Scrollbar(log_frame, command=self.txt_log.yview)
        self.txt_log.config(yscrollcommand=scrollbar.set)

        self.txt_log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botão de Limpar / Resetar
        btn_limpar = tk.Button(
            self.root, 
            text="Limpar Histórico", 
            font=("Arial", 10, "bold"), 
            bg="#e74c3c", 
            fg="white", 
            command=self.limpar_historico
        )
        btn_limpar.pack(pady=10)

    def processar_codigo(self, event=None):
        codigo = self.entry_barcode.get().strip()

        # Limpa o campo imediatamente para a próxima leitura
        self.entry_barcode.delete(0, tk.END)

        if not codigo:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Exemplo de regra de negócio / validação
        if len(codigo) < 5:
            status = "ERRO: Código muito curto ou inválido!"
            self.adicionar_log(f"[{timestamp}] - {codigo} -> {status}", "erro")
            messagebox.showerror("Erro de Validação", f"O código '{codigo}' é inválido!")
            return

        if codigo in self.historico_leituras:
            status = "ALERTA: Código duplicado (já processado)!"
            self.adicionar_log(f"[{timestamp}] - {codigo} -> {status}", "aviso")
            messagebox.showwarning("Aviso", f"O código '{codigo}' já foi escaneado anteriormente!")
            return

        # Se passou nas validações
        self.historico_leituras.add(codigo)
        status = "SUCESSO: Etiqueta aprovada."
        self.adicionar_log(f"[{timestamp}] - {codigo} -> {status}", "sucesso")

    def adicionar_log(self, mensagem, tipo):
        self.txt_log.config(state="normal")
        
        # Cores para destacar no log
        if tipo == "sucesso":
            tag = "sucesso"
            self.txt_log.tag_config("sucesso", foreground="green")
        elif tipo == "erro":
            tag = "erro"
            self.txt_log.tag_config("erro", foreground="red")
        else:
            tag = "aviso"
            self.txt_log.tag_config("aviso", foreground="orange")

        self.txt_log.insert(tk.END, mensagem + "\n", tag)
        self.txt_log.see(tk.END) # Rola automaticamente para o final
        self.txt_log.config(state="disabled")

        # Garante que o foco volte para a caixa de texto da pistola de código
        self.entry_barcode.focus_set()

    def limpar_historico(self):
        self.historico_leituras.clear()
        self.txt_log.config(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.config(state="disabled")
        self.entry_barcode.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = BarcodeQualityControlApp(root)
    root.mainloop()
