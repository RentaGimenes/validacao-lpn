import streamlit as st

# Configuração da página (deixe se já tiver no seu código principal)
# st.set_page_config(layout="wide")

# Título principal
st.markdown("📦 **Validação das informações das Lpn**")

# Abas / Navegação superior simulada
aba1, aba2 = st.tabs(["Painel Principal e Validação", "Concluídos nas Últimas 24h"])

with aba1:
    st.markdown("### 📋 Painel de Solicitações Pendentes")
    
    # Exemplo do Card de Pedido Pendente (como na sua imagem)
    st.markdown(
        """
        <div style="background-color: #1e1e1e; padding: 10px; border-radius: 8px; border: 1px solid #333; width: 160px; text-align: center;">
            <span style="color: #ffcc00; font-weight: bold; font-size: 14px;">Ped. 2</span><br>
            <span style="color: #aaa; font-size: 12px;">Ref: R03</span><br>
            <span style="color: #4CAF50; font-size: 12px; font-weight: bold;">Mat: 65684949</span><br>
            <span style="color: #888; font-size: 11px;">0/1 (0%)</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.write("") # Espaçamento

    # Layout em duas colunas: Esquerda (Formulário e Validação), Direita (Exemplo de LPN)
    col_esq, col_dir = st.columns([1.2, 1])

    with col_esq:
        st.markdown("### 📝 Validar e Dar Baixa na LPN")
        
        # Usamos st.form para permitir que o operador dê os 3 bipes e valide no final
        with st.form(key="form_lpn"):
            nome = st.text_input("Nome", placeholder="Digite seu nome...")
            pedido = st.selectbox("Selecione o Número do Pedido", ["Selecione o pedido...", "Pedido 2 - Ref: R03 (Mat: 65684949)"])
            
            bc1 = st.text_input("1º Código de Barras (LPN)", placeholder="AGUARDANDO ENTRADA")
            bc2 = st.text_input("2º Código de Barras", placeholder="AGUARDANDO ENTRADA")
            bc3 = st.text_input("3º Código de Barras", placeholder="AGUARDANDO ENTRADA")
            
            # Botão de validação do formulário (pode ser acionado por clique ou enter no último campo)
            submitted = st.form_submit_button("Validar e Dar Baixa")

        if submitted:
            if not nome or pedido == "Selecione o pedido..." or not bc1 or not bc2 or not bc3:
                st.warning("⚠️ Por favor, preencha todos os campos e bipa os 3 códigos antes de validar.")
            else:
                # Sua lógica de validação aqui (se houver erro, toca o som da Opção 28)
                st.success("✅ Validação executada com sucesso!")

    with col_dir:
        st.markdown("### 💡 Exemplo de LPN")
        # Aqui você exibe a imagem de exemplo da LPN que estava no seu layout original
        # Substitua o caminho abaixo se você estiver usando st.image com um arquivo local ou URL
        try:
            st.image("caminho_para_sua_imagem_exemplo_lpn.png", use_column_width=True)
        except:
            st.info("*(Imagem de exemplo da etiqueta LPN posicionada aqui)*")
