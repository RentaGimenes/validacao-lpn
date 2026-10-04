import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Sistema de Conferência e Validação", layout="wide")

# Função para tocar o som de erro/alerta (Opção 28)
def tocar_som_erro():
    sound_html = """
        <audio autoplay>
            <source src="https://assets.mixkit.co/active_storage/sfx/2575/2575-preview.mp3" type="audio/mpeg">
        </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# Exemplo de estrutura principal do app
st.title("📦 Sistema de Conferência por Código de Barras")

# Inicializando o estado da sessão se necessário
if "dados" not in st.session_state:
    st.session_state.dados = []

# Área de entrada para simular a leitura do código de barras
codigo_barras = st.text_input("Aguardando leitura do código de barras:", key="input_leitura")

if codigo_barras:
    # Lógica de exemplo para validação (substitua pela sua lógica real de conferência)
    if codigo_barras == "123456":
        st.success(f"Código {codigo_barras} validado com sucesso!")
        st.session_state.dados.append({"Código": codigo_barras, "Status": "OK"})
    else:
        st.error(f"Atenção: Código {codigo_barras} não encontrado ou divergente!")
        tocar_som_erro() # Toca o som da opção 28 automaticamente aqui
        st.session_state.dados.append({"Código": codigo_barras, "Status": "Erro"})

# Exibição dos registros recentes
if st.session_state.dados:
    st.subheader("Histórico de Leituras")
    df = pd.DataFrame(st.session_state.dados)
    st.dataframe(df, use_container_width=True)
