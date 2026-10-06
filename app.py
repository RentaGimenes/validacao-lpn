import tkinter as tk
from tkinter import ttk

class AppPainelPedidos(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Painel de Pedidos - LPN")
        self.geometry("450<span class="math-inline">750")
        self.configure(bg="#111827")  # Fundo escuro estilo o app da foto

        # Estilo geral
        style = ttk.Style()
        style.theme_use("clam")
        
        # --- TÍTULO PRINCIPAL ---
        lbl_titulo = tk.Label(
            self, text="Validação das\nInformações das Lpn", 
            font=("Arial", 18, "bold"), fg="white", bg="#111827", justify="center"
        )
        lbl_titulo.pack(pady=15)

        # --- CONTAINER DE ABAS (Botões) ---
        frame_abas = tk.Frame(self, bg="#111827")
        frame_abas.pack(fill="x", padx=20, pady=5)

        self.btn_pendentes = tk.Button(
            frame_abas, text="⏳ Pedidos Pendentes", font=("Arial", 10, "bold"),
            fg="white", bg="#1f2937", bd=0, relief="flat",
            command=self.mostrar_pendentes
        )
        self.btn_pendentes.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_concluidos = tk.Button(
            frame_abas, text="✅ Pedidos Concluídos", font=("Arial", 10, "bold"),
            fg="white", bg="#1f2937", bd=0, relief="flat",
            command=self.mostrar_concluidos
        )
        self.btn_concluidos.pack(side="left", expand=True, fill="x", padx=2)

        # Linha indicadora da aba ativa (barra vermelha embaixo)
        self.linha_aba = tk.Frame(self, bg="#ef4444", height=3)
        self.linha_aba.pack(fill="x", padx=20)

        # --- ÁREA DE CONTEÚDO DINÂMICO (Onde alternam os cards) ---
        self.frame_conteudo = tk.Frame(self, bg="#111827")
        self.frame_conteudo.pack(fill="both", expand=True, padx=20, pady=10)

        # --- SEÇÃO DE VALIDAÇÃO (A parte de baixo que some nos concluídos) ---
        self.frame_validacao = tk.Frame(self, bg="#111827")
        self.construir_secao_validacao()
        
        # Inicia na aba de Pendentes
        self.mostrar_pendentes()

    def construir_secao_validacao(self):
        # Título da seção de validação
        lbl_val = tk.Label(
            self.frame_validacao, text="📝 Validar e Dar Baixa na LPN", 
            font=("Arial", 14, "bold"), fg="white", bg="#111827", anchor="w"
        )
        lbl_val.pack(fill="x", pady=(10, 5))

        # Campo Nome
        tk.Label(self.frame_validacao, text="Nome", font=("Arial", 10), fg="white", bg="#111827", anchor="w").pack(fill="x")
        self.entry_nome = tk.Entry(self.frame_validacao, font=("Arial", 11), bg="#1f2937", fg="white", insertbackground="white", relief="flat")
        self.entry_nome.pack(fill="x", pady=(2, 10), ipady=5)

        # Campo 1º Código de Barras
        tk.Label(self.frame_validacao, text="1º Código de Barras (LPN)", font=("Arial", 10), fg="white", bg="#111827", anchor="w").pack(fill="x")
        self.entry_lpn1 = tk.Entry(self.frame_validacao, font=("Arial", 11), bg="#1f2937", fg="white", insertbackground="white", relief="flat")
        self.entry_lpn1.pack(fill="x", pady=(2, 10), ipady=5)

        # Botão Iniciar Validação
        btn_iniciar = tk.Button(
            self.frame_validacao, text="INICIAR VALIDAÇÃO", font=("Arial", 11, "bold"),
            fg="#10b981", bg="#111827", bd=2, relief="solid", highlightcolor="#10b981"
        )
        btn_iniciar.pack(fill="x", pady=10, ipady=8)

    def limpar_conteudo(self):
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()

    def mostrar_pendentes(self):
        # Atualiza estilo visual dos botões das abas
        self.btn_pendentes.config(fg="#ef4444")
        self.btn_concluidos.config(fg="white")
        
        # Posiciona a linha vermelha à esquerda (Pendentes)
        self.linha_aba.pack_configure(anchor="w")

        # Limpa e popula o conteúdo de Pendentes
        self.limpar_conteudo()
        
        lbl_info = tk.Label(
            self.frame_conteudo, text="Nenhum pedido pendente no momento.", 
            font=("Arial", 11), fg="#9ca3af", bg="#1f2937", padx=15, pady=20
        )
        lbl_info.pack(fill="x", pady=5)

        # **MOSTRA** a seção de validação embaixo quando estiver em Pendentes
        self.frame_validacao.pack(fill="x", padx=20, pady=10)

    def mostrar_concluidos(self):
        # Atualiza estilo visual dos botões das abas
        self.btn_pendentes.config(fg="white")
        self.btn_concluidos.config(fg="#ef4444")
        
        # Limpa e popula o conteúdo de Concluídos
        self.limpar_conteudo()
        
        lbl_info = tk.Label(
            self.frame_conteudo, text="Nenhum pedido concluído nas últimas 24 horas.", 
            font=("Arial", 11), fg="#9ca3af", bg="#1f2937", padx=15, pady=20
        )
        lbl_info.pack(fill="x", pady=5)

        # **ESCONDE** completamente a seção de validação embaixo quando estiver em Concluídos
        self.frame_validacao.pack_forget()

if __name__ == "__main__":
    app = AppPainelPedidos()
    app.mainloop()
