import tkinter as tk
from tkinter import messagebox

# Se estiver usando Pillow para carregar imagens/GIFs, descomente a linha abaixo:
# from PIL import Image, ImageTk

class AppLPN(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Validação de LPN")
        self.geometry("500x400")
        self.config(bg="#f0f0f0")
        
        # Variável para guardar o último código lido
        self.ultimo_codigo = ""
        
        # --- TELA PRINCIPAL ---
        
        # Título do app
        lbl_titulo = tk.Label(self, text="Sistema de Validação de LPN", font=("Arial", 14, "bold"), bg="#f0f0f0")
        lbl_titulo.pack(pady=20)
        
        # Campo de entrada para a pistola de código de barras / digitação
        lbl_instrucao = tk.Label(self, text="Bipe ou digite a LPN:", font=("Arial", 10), bg="#f0f0f0")
        lbl_instrucao.pack(anchor="w", padx=40)
        
        self.entry_lpn = tk.Entry(self, font=("Arial", 12))
        self.entry_lpn.pack(fill="x", padx=40, pady=5)
        self.entry_lpn.focus() # Já deixa o cursor piscando aqui
        
        # Evento para quando apertar Enter (já valida automático)
        self.entry_lpn.bind("<Return>", self.processar_lpn)
        
        # Botão de validar manual caso precise
        btn_validar = tk.Button(self, text="Validar", command=self.processar_lpn, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        btn_validar.pack(pady=10)
        
        # Área de status/resultado para o operador ver
        self.lbl_status = tk.Label(self, text="Aguardando leitura...", font=("Arial", 11), bg="#f0f0f0", fg="#666")
        self.lbl_status.pack(pady=20)
        
        
        # --- RODAPÉ COM O SONIC E A MENSAGEM ---
        
        # Frame que fica preso na parte de baixo
        footer_frame = tk.Frame(self, bg="#e0e0e0", pady=8)
        footer_frame.pack(side="bottom", fill="x")
        
        # Container interno para centralizar tudo junto (Sonic + Texto)
        content_container = tk.Frame(footer_frame, bg="#e0e0e0")
        content_container.pack(anchor="center")
        
        # Carregamento do Sonic (Exemplo usando texto/emoji se não tiver o GIF carregado, 
        # mas deixei pronto para imagem/GIF logo abaixo)
        
        # SE FOR USAR IMAGEM/GIF COM PIL:
        # img_file = Image.open("caminho_do_sonic.gif")
        # self.sonic_img = ImageTk.PhotoImage(img_file)
        # self.lbl_sonic = tk.Label(content_container, image=self.sonic_img, bg="#e0e0e0")
        
        # Usando um label simples caso esteja testando sem a imagem física agora:
        self.lbl_sonic = tk.Label(content_container, text="🦔💨", font=("Arial", 16), bg="#e0e0e0")
        self.lbl_sonic.pack(side="left", padx=5)
        
        # Mensagem pedida no rodapé
        lbl_mensagem = tk.Label(
            content_container, 
            text="Validação de Lpn a todo vapor!", 
            font=("Arial", 10, "italic"), 
            bg="#e0e0e0", 
            fg="#333"
        )
        lbl_mensagem.pack(side="left", padx=5)

    def limpar_campos(self):
        """Função simples para limpar o input e deixar pronto para a próxima LPN"""
        self.entry_lpn.delete(0, tk.END)
        self.entry_lpn.focus()

    def processar_lpn(self, event=None):
        """Pega o código digitado/biopado, valida e já limpa para a próxima"""
        codigo = self.entry_lpn.get().strip()
        
        if not codigo:
            messagebox.showwarning("Aviso", "Nenhum código detectado!")
            return
            
        self.ultimo_codigo = codigo
        
        # Aqui entra a sua lógica de comparação com a planilha/sistema
        # Exemplo simulado:
        self.lbl_status.config(text=f"LPN '{codigo}' validada com sucesso!", fg="green")
        
        # Limpa automaticamente o campo para o operador escanear a próxima etiqueta
        self.limpar_campos()

if __name__ == "__main__":
    app = AppLPN()
    app.mainloop()
