import streamlit as st

# Configuração da página
st.set_page_config(page_title="Validação LPN", page_icon="📦", layout="centered")

# Estilo visual personalizado (tema escuro idêntico ao seu print)
st.markdown("""
    <style>
    .main { background-color: #111827; }
    .stApp { background-color: #111827; color: white; }
    h1, h2, h3 { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown("<h2 style='text-align: center;'>Validação das Informações das Lpn</h2>", unsafe_allow_html=True)
st.markdown("---")

st.markdown("### 📋 PAINEL DE PEDIDOS")
st.markdown("Selecione o pedido nas abas abaixo:")

# Abas do Streamlit
aba_pendentes, aba_concluidos = st.tabs(["⏳ Pedidos Pendentes", "✅ Pedidos Concluídos"])

# ==========================================
# ABA 1: PEDIDOS PENDENTES (Com Validação)
# ==========================================
with aba_pendentes:
    if st.button("🔄 ATUALIZAR PEDIDOS", key="atualizar_pend"):
        st.toast("Pedidos atualizados!")

    st.info("Nenhum pedido pendente no momento.")
    
    st.markdown("---")
    st.markdown("### 📝 Validar e Dar Baixa na LPN")
    
    # Formulário de Validação (Aparece apenas na aba de Pendentes)
    with st.form("form_validacao"):
        nome = st.text_input("Nome", placeholder="Digite seu nome...")
        lpn1 = st.text_input("1º Código de Barras (LPN)", placeholder="")
        lpn2 = st.text_input("2º Código de Barras (LPN)", placeholder="")
        lpn3 = st.text_input("3º Código de Barras (LPN)", placeholder="")
        
        submitted = st.form_submit_button("INICIAR VALIDAÇÃO")
        if submitted:
            if not nome or not lpn1:
                st.warning("⚠️ Para iniciar, por favor preencha o nome e pelo menos a primeira LPN.")
            else:
                st.success("Validação iniciada com sucesso!")

# ==========================================
# ABA 2: PEDIDOS CONCLUÍDOS (Apenas os Cards/Histórico, sem validação)
# ==========================================
with aba_concluidos:
    if st.button("🔄 ATUALIZAR PEDIDOS", key="atualizar_conc"):
        st.toast("Histórico atualizado!")

    # Apenas o aviso ou os cards concluídos, SEM NENHUMA parte de validação embaixo
    st.info("Nenhum pedido concluído nas últimas 24 horas.")
    
    # Aqui você pode futuramente renderizar os cards dos pedidos concluídos quando houverem registros.
