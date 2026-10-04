       margin-bottom: 15px;
   }

    /* ESTILO DO BOTÃO DE VALIDAÇÃO COM O MODELO DA REFERÊNCIA */
    /* ESTILO DO BOTÃO DE VALIDAÇÃO EM FORMATO QUADRADINHO COM REFERÊNCIA */
   div.stButton > button {
       background-color: #111a16 !important;
       color: #2ecc71 !important;
        font-size: 16px !important;
        font-size: 15px !important;
       font-weight: bold !important;
        height: 55px !important;
        height: 60px !important;
       width: 100% !important;
        max-width: 220px !important;
       border-radius: 12px !important;
       border: 2px solid #2ecc71 !important;
       box-shadow: 0px 0px 10px rgba(46, 204, 113, 0.3) !important;
       transition: 0.3s;
        display: block;
        margin: 0 auto;
   }
   div.stButton > button:hover {
       background-color: #1b2e23 !important;
@@ -380,7 +383,7 @@ def obter_quantidade_total_lpns(r):
st.markdown("---")

else:
    # SEÇÃO ALTERADA PARA "PEDIDOS DE LPN" CONFORME SOLICITADO
    # SEÇÃO "PEDIDOS DE LPN"
st.subheader("📋 PEDIDOS DE LPN")

col_tit_painel, col_btn_att = st.columns([5, 1.5])
@@ -485,7 +488,7 @@ def obter_quantidade_total_lpns(r):

st.markdown("---")

    # Layout de 3 Colunas: Esquerda (Inputs), Meio (Modelo de LPN alinhado), Direita (Alerta e Botão)
    # Layout de 3 Colunas: Esquerda (Inputs), Meio (Modelo de LPN alinhado), Direita (Alerta e Botão Único)
col_form, col_img, col_acao = st.columns([1.2, 1.2, 1.3], gap="large")

with col_form:
@@ -580,7 +583,7 @@ def obter_quantidade_total_lpns(r):
if len(lidas_atualmente_btn) > 0:
texto_botao_validar = "VALIDAR PRÓXIMA LPN"

        # BOTÃO COM O NOVO ESTILO NEON
        # BOTÃO ÚNICO COM O ESTILO QUADRADINHO CUSTOMIZADO
btn_validar_clicado = st.button(texto_botao_validar, key="btn_validar_lpn_custom", use_container_width=True)

if btn_validar_clicado:
