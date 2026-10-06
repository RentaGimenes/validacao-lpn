import tkinter as tk
from tkinter import messagebox, ttk

# Importações opcionais caso você utilize integração com planilhas (ex: openpyxl ou pandas)
# import openpyxl


class AppValidacaoLPN:

  def __init__(self, root):
    self.root = root
    self.root.title("Validação de LPN e Códigos de Barras")
    self.root.geometry("600x450")
    self.root.config(bg="#f0f0f0")

    self.criar_componentes()

  def criar_componentes(self):
    # Título Principal
    titulo = tk.Label(
        self.root,
        text="Sistema de Validação - Rigor",
        font=("Arial", 16, "bold"),
        bg="#f0f0f0",
        fg="#333333",
    )
    titulo.pack(pady=20)

    # Frame para Entrada de Dados
    frame_entrada = tk.Frame(self.root, bg="#f0f0f0")
    frame_entrada.pack(pady=10)

    lbl_codigo = tk.Label(
        frame_entrada,
        text="Escaneie ou Digite o Lote/LPN:",
        font=("Arial", 11),
        bg="#f0f0f0",
    )
    lbl_codigo.pack(anchor="w", pady=5)

    self.entry_codigo = tk.Entry(frame_entrada, font=("Arial", 14), width=35)
    self.entry_codigo.pack(pady=5)
    self.entry_codigo.focus()
    # Associa a tecla Enter para disparar a validação automaticamente (comportamento de leitor de código de barras)
    self.entry_codigo.bind("<Return>", lambda event: self.validar_codigo())

    # Botão de Validação
    btn_validar = tk.Button(
        self.root,
        text="Validar Código",
        font=("Arial", 11, "bold"),
        bg="#4CAF50",
        fg="white",
        width=20,
        command=self.validar_codigo,
    )
    btn_validar.pack(pady=15)

    # Caixa de Log / Histórico de Leituras
    frame_log = tk.Frame(self.root)
    frame_log.pack(pady=10, fill="both", expand=True, padx=20)

    lbl_log = tk.Label(
        frame_log, text="Histórico de Validações:", font=("Arial", 10, "bold")
    )
    lbl_log.pack(anchor="w")

    self.txt_log = tk.Text(
        frame_log, height=8, font=("Courier", 10), state="disabled"
    )
    self.txt_log.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(frame_log, command=self.txt_log.yview)
    scrollbar.pack(side="right", fill="y")
    self.txt_log.config(yscrollcommand=scrollbar.set)

  def formatar_lote_lido_rigor(self, codigo):
    """Função dedicada a tratar, formatar ou extrair caracteres específicos

    do código escaneado de acordo com o padrão do Rigor.
    """
    codigo_limpo = codigo.strip()

    # Exemplo de manipulação (ajuste conforme a regra do seu projeto, ex: fatiamento de string):
    # Se o código contiver prefixos ou caracteres especiais indesejados:
    # codigo_limpo = codigo_limpo.upper()

    return codigo_limpo

  def validar_codigo(self):
    codigo_bruto = self.entry_codigo.get()

    if not codigo_bruto:
      messagebox.showwarning(
          "Aviso", "Por favor, escaneie ou digite um código válido!"
      )
      return

    # Chamada correta da função de formatação
    codigo_formatado = self.formatar_lote_lido_rigor(codigo_bruto)

    # Aqui você pode inserir a lógica para che
