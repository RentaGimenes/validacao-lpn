import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # Necessário para carregar arquivos PNG/JPG

class AppLPN(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Validação de LPN")
        self.geometry("500x450")
        self.config(bg="#f0f0f0")
        
        # Lista simulada para guardar LPNs já lidas (para testar a duplicada)
        self.lpns_processadas = []
        
        # --- CARREGAR IMAGENS ---
        try:
            # Carrega a imagem de LPN duplicada que você subiu
            img_dup = Image.open("lpnduplicada.PNG")
            img_dup = img_dup.resize((24, 24))  # Redimensiona se precisar ajustar o tamanho
            self.icone_duplicada = ImageTk.PhotoImage(img_dup)
        except Exception as e:
            self.icone_duplicada = None
            print("Aviso: Não foi possível carregar a imagem lpnduplicada.PNG", e)

        # --- TELA PRINCIPAL ---
        
        # Título do app
        lbl_titulo = tk.Label(self, text="Sistema de Validação de LPN", font=("Arial", 14, "bold"), bg="#f0f0f0")
        lbl_titulo.pack(pady=15)
        
        # Campo de entrada para a pistola de código de barras
        lbl_instrucao = tk.Label(self, text="Bipe ou digite a LPN:", font=("Arial", 10), bg="#f0f0f0")
        lbl_instrucao.pack(anchor="w", padx=40)
        
        self.entry_lpn = tk.Entry(self, font=("Arial", 12))
        self.entry_lpn.pack(fill="x", padx=40, pady=5)
        self.entry_lpn.focus()  # Deixa o cursor pronto para bipar
        
        # Evento do Enter para validar na hora
        self.entry_lpn.bind("<Return>", self.processar_lpn)
        
        # Botão validar
        btn_validar = tk.Button(self, text="Validar", command=self.processar_lpn, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        btn_validar.pack(pady=10)
        
        # Área de status/resultado
        self.lbl_status = tk.Label(self, text="Aguardando leitura...", font=("Arial", 11), bg="#f0f0f0", fg="#666")
        self.lbl_status.pack(pady=15)
        
        # Label extra caso queira mostrar o icone de duplicado na tela de erros
        self.lbl_aviso_icone = tk.Label(self, bg="#f0f0f0")
        self.lbl_aviso_icone.pack(pady=5)
        
        
        # --- RODAPÉ COM O SONIC E A MENSAGEM ---
        
        footer_frame = tk.Frame(self, bg="#e0e0e0", pady=8)
        footer_frame.pack(side="bottom", fill="x")
        
        content_container = tk.Frame(footer_frame, bg="#e0e0e0")
        content_container.pack(anchor="center")
        
        # Sonic no rodapé (usando emoji ou trocando por imagem se preferir)
        self.lbl_sonic = tk.Label(content_container, text="🦔💨", font=("Arial", 16), bg="#e0e0e0")
        self.lbl_sonic.pack(side="left", padx=5)
        
        # Mensagem fixa no rodapé
        lbl_mensagem = tk.Label(
            content_container, 
            text="Validação de Lpn a todo vapor!", 
            font=("Arial", 10, "italic"), 
            bg="#e0e0e0", 
            fg="#333"
        )
        lbl_mensagem.pack(side="left", padx=5)

    def limpar_para_proxima(self):
        """Limpa o campo de texto e foca para a próxima LPN (já tem a função pronta!)"""
        self.entry_lpn.delete(0, tk.END)
        self.entry_lpn.focus()

    def processar_lpn(self, event=None):
        """Valida se a LPN é nova ou se já foi bipada (duplicada)"""
        codigo = self.entry_lpn.get().strip()
        
        if not codigo:
            messagebox.showwarning("Aviso", "Nenhum código detectado!")
            return
            
        # Verifica se a LPN já existe na lista (simulando LPN duplicada)
        if codigo in self.lpns_processadas:
            # FALHA: LPN Duplicada! Mostra a imagem dedicada que você colocou
            self.lbl_status.config(text=f"ERRO: LPN '{codigo}' já foi lida (Duplicada)!", fg="red")
            
            if self.icone_duplicada:
                self.lbl_aviso_icone.config(image=self.icone_duplicada, text=" ⚠️ LPN Duplicada", compound="left", fg="red")
            else:
                self.lbl_aviso_icone.config(text="⚠️ LPN Duplicada!", fg="red")
        else:
            # SUCESSO: LPN Nova
            self.lpns_processadas.append(codigo)
            self.lbl_status.config(text=f"LPN '{codigo}' validada com sucesso!", fg="green")
            self.lbl_aviso_icone.config(image="", text="") # Limpa o aviso de erro anterior
            
        # Limpa automaticamente para a próxima leitura da pistola
        self.limpar_para_proxima()

if __name__ == "__main__":
    app = AppLPN()
    app.mainloop()
