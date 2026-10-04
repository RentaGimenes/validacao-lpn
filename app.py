import streamlit as st

# Configuração da página (caso já não tenha no seu topo)
st.set_page_config(
    page_title="Validação de LPN", page_icon="📝", layout="centered"
)

st.title("📝 Validar e Dar Baixa na LPN")

# Exemplo de campo de Nome e Pedido (ajuste conforme seu código original)
nome = st.text_input("Nome", value="renata")
st.write(
    "🎯 Pedido Selecionado: Pedido 3 (Linha: R03 - Mat: DOVE SH NUTRI+TRI-OLEO"
)

# 1. Garante que as chaves dos códigos de barras existam no session_state
for k in ["input_bc1", "input_bc2", "input_bc3"]:
  if k not in st.session_state:
    st.session_state[k] = ""

# 2. Inputs vinculados diretamente ao session_state via chave (key)
bc1 = st.text_input("1º Código de Barras (LPN)", key="input_bc1")
bc2 = st.text_input("2º Código de Barras", key="input_bc2")
bc3 = st.text_input("3º Código de Barras", key="input_bc3")

# Exemplo de progresso (substitua pela sua lógica real)
st.write("Progresso: 0 de 5 LPNs (0%)")
st.progress(0.0)

# 3. Botão de Validação
if st.button("Validar LPN", type="primary", use_container_width=True):
  # Valida se os três campos estão preenchidos
  if not bc1.strip() or not bc2.strip() or not bc3.strip():
    st.warning("Preencha os 3 códigos de barras.")
  else:
    # --- INSIRA SUA LÓGICA DE VALIDAÇÃO/BAIXA AQUI ---
    # (ex: salvar no banco, atualizar planilha, etc.)
    # ------------------------------------------------

    st.success("LPN validada e baixada com sucesso!")

    # Limpa os campos atribuindo string vazia ao session_state
    st.session_state["input_bc1"] = ""
    st.session_state["input_bc2"] = ""
    st.session_state["input_bc3"] = ""

    # Força a recriação da tela para esvaziar os inputs visualmente e sumir com o aviso
    st.rerun()
