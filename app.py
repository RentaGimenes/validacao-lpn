import os
import tkinter as tk


class AppVerificadorLPN:

  def __init__(self, root):
    self.root = root
    self.root.title("Verificador de LPN e Divergência")
    self.root.geometry("1100x650")
    self.root.configure(bg="#181a1b")  # Fundo escuro do painel

    # Lista para guardar os quadros da animação e o índice atual
    self.frames_sonic = []
    self.indice_atual = 0

    # Monta a tela e carrega o sonic
    self.criar_interface()
    self.carregar_frames_sonic()
    self.animar()

  def criar_interface(self):
    # Caixa amarela de aviso no topo
    frame_aviso = tk.Frame(
        self.root,
        bg="#181a1b",
        highlightbackground="#ffd700",
        highlightthickness=1,
    )
    frame_aviso.pack(fill="x", padx=15, pady=15)

    # Texto do aviso de lpn ilustrativa
    texto_aviso = (
        "⚠️ LPNS MERAMENTE ILUSTRATIVAS\n"
        "SEUS VALORES DEVEM SER CONSIDERADOS APENAS COMO EXEMPLO PARA FACILITAR"
        " A VISUALIZAÇÃO DA DIVERGÊNCIA."
    )
    lbl_aviso = tk.Label(
        frame_aviso,
        text=texto_aviso,
        fg="#ffd700",
        bg="#181a1b",
        font=("Arial", 10, "bold"),
        justify="left",
        padx=10,
        pady=10,
    )
    lbl_aviso.pack(side="left", fill="both", expand=True)

    # Label onde o gif do sonic vai ficar se mexendo
    self.lbl_sonic = tk.Label(frame_aviso, bg="#181a1b")
    self.lbl_sonic.pack(side="right", padx=10, pady=5)

    # Linha que mostra a LPN atual que foi lida
    frame_lpn = tk.Frame(self.root, bg="#181a1b")
    frame_lpn.pack(fill="x", padx=15, pady=10)

    lbl_icone_lpn = tk.Label(frame_lpn, text="📦", bg="#181a1b", font=("Arial", 14))
    lbl_icone_lpn.pack(side="left", padx=(0, 5))

    self.lbl_lpn_titulo = tk.Label(
        frame_lpn,
        text="LPN Atual:",
        fg="white",
        bg="#181a1b",
        font=("Arial", 12, "bold"),
    )
    self.lbl_lpn_titulo.pack(side="left")

    self.lbl_lpn_valor = tk.Label(
        frame_lpn,
        text="00378911505103650406",
        fg="#00ff7f",
        bg="#181a1b",
        font=("Arial", 12, "bold"),
    )
    self.lbl_lpn_valor.pack(side="left", padx=10)

    # Campo de texto para o leitor de código de barras mandar a próxima LPN
    frame_entrada = tk.Frame(self.root, bg="#181a1b")
    frame_entrada.pack(fill="x", padx=15, pady=20)

    lbl_instrucao = tk.Label(
        frame_entrada,
        text="Bipe a próxima LPN ou digite aqui:",
        fg="white",
        bg="#181a1b",
        font=("Arial", 10),
    )
    lbl_instrucao.pack(anchor="w", pady=5)

    self.entry_codigo = tk.Entry(
        frame_entrada,
        font=("Arial", 12),
        bg="#2b2b2b",
        fg="white",
        insertbackground="white",
    )
    self.entry_codigo.pack(fill="x", ipady=5)
    self.entry_codigo.focus()

    # Aperta enter para processar o código lido
    self.entry_codigo.bind("<Return>", self.processar_codigo)

  def carregar_frames_sonic(self):
    pasta_frames = "sonicgif"

    # Pega os frames da pasta de 00 até 19
    for i in range(20):
      nome_arquivo = os.path.join(
          pasta_frames, f"frame_{i:02d}_delay-0.05s.png"
      )
      if os.path.exists(nome_arquivo):
        try:
          img = tk.PhotoImage(file=nome_arquivo)
          self.frames_sonic.append(img)
        except Exception as e:
          print("Erro ao carregar imagem:", e)

    if not self.frames_sonic:
      self.lbl_sonic.config(
          text="[Erro: coloque os frames na pasta sonicgif]", fg="red"
      )

  def animar(self):
    if self.frames_sonic:
      # Pega o frame da vez e joga na label
      frame_atual = self.frames_sonic[self.indice_atual]
      self.lbl_sonic.config(image=frame_atual)

      # Passa para o próximo frame
      self.indice_atual = (self.indice_atual + 1) % len(self.frames_sonic)

    # Tempo de 50ms para rodar certinho com o delay original dos quadros
    self.root.after(50, self.animar)

  def processar_codigo(self, event):
    # Pega o que foi bipado no leitor
    codigo_lido = self.entry_codigo.get().strip()

    if not codigo_lido:
      return

    # Atualiza o visor da LPN atual na tela
    self.lbl_lpn_valor.config(text=codigo_lido)

    # Limpa a caixa de texto para a próxima leitura (próxima lpnw)
    self.entry_codigo.delete(0, tk.END)

    # Aqui você pode colocar a função que verifica a divergência na planilha
    self.verificar_divergencia(codigo_lido)

  def verificar_divergencia(self, lpn):
    print(f"LPN processada e limpa para a próxima: {lpn}")


if __name__ == "__main__":
  root = tk.Tk()
  app = AppVerificadorLPN(root)
  root.mainloop()
