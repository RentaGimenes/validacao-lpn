import streamlit as st

# Configuração básica da página
st.set_page_config(page_title="Validador de Códigos", page_icon="📦", layout="centered")

st.title("📦 Leitor e Validador de Lote")
st.write("Bipe os três códigos em sequência. Ao enviar o terceiro, a validação é feita e os campos são limpos.")

# Inicializa as variáveis no estado da sessão do Streamlit se não existirem
if "etapa" not in st.session_state:
    st.session_state.etapa = 1
if "c1" not in st.session_state:
    st.session_state.c1 = ""
if "c2" not in st.session_state:
    st.session_state.c2 = ""
if "c3" not in st.session_state:
    st.session_state.c3 = ""

# Função para avançar ou processar ao pressionar Enter / submeter
def lidar_envio():
    # Etapa 1: Preencheu o primeiro código
    if st.session_state.etapa == 1:
        if st.session_state.input_atual.strip():
            st.session_state.c1 = st.session_state.input_atual.strip()
            st.session_state.etapa = 2
            st.session_state.input_atual = "" # Limpa o input para o próximo
        else:
            st.warning("Opa! Preencha o primeiro código.")

    # Etapa 2: Preencheu o segundo código
    elif st.session_state.etapa == 2:
        if st.session_state.input_atual.strip():
            st.session_state.c2 = st.session_state.input_atual.strip()
            st.session_state.etapa = 3
            st.session_state.input_atual = ""
        else:
            st.warning("Opa! Preencha o segundo código.")

    # Etapa 3: Preencheu o terceiro código (Validação e Limpeza)
    elif st.session_state.etapa == 3:
        if st.session_state.input_atual.strip():
            st.session_state.c3 = st.session_state.input_atual.strip()
            
            # Pega todos os códigos do lote atual
            c1 = st.session_state.c1
            c2 = st.session_state.c2
            c3 = st.session_state.c3

            # TODO: Colocar aqui a lógica de validação ou consulta na planilha
            st.success(f"Lote validado com sucesso! -> {c1} | {c2} | {c3}")

            # Reseta tudo para reiniciar o ciclo do zero
            st.session_state.c1 = ""
            st.session_state.c2 = ""
            st.session_state.c3 = ""
            st.session_state.etapa = 1
            st.session_state.input_atual = ""
        else:
            st.warning("Opa! Faltou o terceiro código.")

# Mostra o status atual do lote que está a ser montado
if st.session_state.etapa > 1:
    st.info(f"**1º Código lido:** {st.session_state.c1}")
if st.session_state.etapa > 2:
    st.info(f"**2º Código lido:** {st.session_state.c2}")

# Mensagem orientando qual código deve ser bipado agora
instrucoes = {
    1: "Bipe o **primeiro** código e aperte Enter:",
    2: "Bipe o **segundo** código e aperte Enter:",
    3: "Bipe o **terceiro** código e aperte Enter para validar:"
}

# Campo de texto único dinâmico que recebe a leitura do leitor de código de barras
st.text_input(
    instrucoes[st.session_state.etapa], 
    key="input_atual", 
    on_change=lidar_envio,
    autofocus=True
)

# Botão opcional caso queira reiniciar manualmente
if st.button("🔄 Reiniciar / Limpar Ciclo"):
    st.session_state.c1 = ""
    st.session_state.c2 = ""
    st.session_state.c3 = ""
    st.session_state.etapa = 1
    st.session_state.input_atual = ""
    st.rerun()
