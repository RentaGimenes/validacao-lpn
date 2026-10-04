import streamlit as st

# Inicializa as variáveis no session_state se não existirem
if "bc1" not in st.session_state:
    st.session_state.bc1 = ""
if "bc2" not in st.session_state:
    st.session_state.bc2 = ""
if "bc3" not in st.session_state:
    st.session_state.bc3 = ""

# Funções de callback para avançar o foco automaticamente quando o Enter for disparado pela pistola
def processar_bc1():
    # O valor digitado/bipado já fica salvo automaticamente no session_state.bc1
    pass

def processar_bc2():
    pass

def processar_bc3():
    # Ao bipar o terceiro e a pistola enviar o Enter, esta função roda na hora!
    if st.session_state.bc1 and st.session_state.bc2 and st.session_state.bc3:
        # Aqui você coloca sua validação (se der erro, toca o som da Opção 28)
        st.success("Todos os códigos lidos! Validando...")

# Interface limpa e nativa do Streamlit
st.title("Validação de LPN / Códigos de Barras")

# Campo 1
st.text_input("1º Código de Barras", key="bc1", on_change=processar_bc1)

# Campo 2
st.text_input("2º Código de Barras", key="bc2", on_change=processar_bc2)

# Campo 3 (ao ler este, dispara a validação final sozinha por causa do Enter da pistola)
st.text_input("3º Código de Barras", key="bc3", on_change=processar_bc3)

# Botão opcional caso queira manter redundância
if st.button("Validar Manualmente"):
    processar_bc3()
