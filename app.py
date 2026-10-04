import streamlit as st

# Configuração da página para ocupar a largura toda
st.set_page_config(layout="wide", page_title="Validar e Dar Baixa na LPN")

# Estilos em CSS para deixar só o botão de validação verde e ajustar a caixa de aviso
st.markdown(
    """
    <style>
    div.row-widget.stButton > button {
        background-color: #0d2311 !important;
        color: #2ecc71 !important;
        border: 2px solid #2ecc71 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        width: 100%;
        padding: 0.75rem;
    }
    div.row-widget.stButton > button:hover {
        background-color: #2ecc71 !important;
        color: #ffffff !important;
    }
    
    .aviso-box {
        background-color: rgba(139, 0, 0, 0.2);
        border: 1px dashed #ff4d4d;
        color: #ff4d4d;
        padding: 8px 12px;
        border-radius: 6px;
        text-align: center;
        font-weight: bold;
        font-size: 11px;
        max-width: 320px;
        margin: 0 auto 15px auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Título principal do app
st.markdown("### 📝 Validar e Dar Baixa na LPN")

# Layout dividido em 3 colunas (Inputs, Exemplo LPN, Avisos e Ações)
col_inputs, col_exemplo, col_acoes = st.columns([1.1, 1.4, 1.1])

# Coluna da esquerda: Campos de texto para preenchimento
with col_inputs:
    nome = st.text_input("Nome", placeholder="Digite seu nome...")
    lpn_1 = st.text_input("1º Código de Barras (LPN)", placeholder="Código de Barras")
    lpn_2 = st.text_input("2º Código de Barras", placeholder="Código de Barras")
    lpn_3 = st.text_input("3º Código de Barras", placeholder="Código de Barras")

# Coluna do meio: Exemplo visual da LPN (maior)
with col_exemplo:
    st.markdown(
        """
        <div style="background-color: #ffffff; width: 100%; max-width: 440px; height: 420px; border-radius: 6px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #333333; font-weight: bold; border: 1px solid #ccc; margin: 0 auto;">
            <span style="font-size: 15px; margin-bottom: 8px;">EXEMPLO DE LPN</span>
            <span style="font-size: 12px; color: #666;">[ Insira a imagem da etiqueta aqui ]</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Coluna da direita: Aviso e o botão verde
with col_acoes:
    # Aviso compacto logo acima do botão
    st.markdown(
        """
        <div class="aviso-box">
            ⚠ POR FAVOR, SELECIONE UM PEDIDO PARA CONFIRMAR AS LPN
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    
    # Botão de validação (único botão verde na tela)
    if st.button("VALIDAR LPN"):
        # Lógica simples de validação ao clicar
        if not nome or not lpn_1:
            st.warning("Preencha os campos obrigatórios para continuar!")
        else:
            st.success("LPN validada com sucesso!")
