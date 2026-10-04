import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # Necessário para carregar arquivos PNG no Tkinter

def acao_validar():
    """Função executada ao clicar no botão de validar."""
    messagebox.info("Sucesso", "O botão validar foi clicado!")
    # Coloque aqui a sua lógica (ex: comparar dados, ler código de barras, etc.)

def criar_app():
    # Inicializa a janela principal
    root = tk.Tk()
    root.title("Aplicativo de Validação")
    root.geometry("400x250")

    # Contêiner principal (Frame) para agrupar os itens e alinhar à esquerda
    container_itens = tk.Frame(root)
    # anchor='w' empurra o frame para o oeste (esquerda) da janela com margens zeradas
    container_itens.pack(anchor="w", padx=10, pady=10)

    try:
        # Carrega a imagem 'validar.png' usando Pillow (PIL)
        img_original = Image.open("validar.png")
        
        # Opcional: redimensione a imagem se achar necessário (ex: largura 120, altura proporcional)
        # img_original = img_original.resize((120, 40), Image.Resampling.LANCZOS)
        
        img_validar = ImageTk.PhotoImage(img_original)
    except Exception as e:
        # Caso ocorra algum erro ao carregar a imagem (ex: arquivo não encontrado)
        print(f"Erro ao carregar a imagem: {e}")
        img_validar = None

    # 1. Botão de Imagem (usando Label com bind ou Button com imagem)
    if img_validar:
        # Usar Button com image no Tkinter
        btn_validar = tk.Button(
            container_itens, 
            image=img_validar, 
            command=acao_validar,
            borderwidth=0,     # Remove borda padrão
            highlightthickness=0,
            relief="flat",
            cursor="hand2"     # Muda o cursor para mãozinha ao passar por cima
        )
        # Mantém uma referência para a imagem não sumir por causa do Garbage Collector do Python
        btn_validar.image = img_validar 
    else:
        # Botão de texto de segurança caso a imagem falhe
        btn_validar = tk.Button(container_itens, text="Validar", command=acao_validar)

    # Posiciona o botão à esquerda dentro do contêiner
    btn_validar.pack(side=tk.LEFT, padx=(0, 10))

    # 2. O segundo item ao lado (exemplo: um rótulo/texto)
    outro_item = tk.Label(container_itens, text="Outro item ao lado", font=("Arial", 11))
    
    # Posiciona o segundo item logo à esquerda/ao lado do botão
    outro_item.pack(side=tk.LEFT)

    # Inicia o loop da aplicação
    root.mainloop()

if __name__ == "__main__":
    criar_app()
