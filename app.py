# ==========================================
# ESTILOS VISUAIS (CSS) E JAVASCRIPT
# ==========================================
st.markdown("""
    <style>
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 6rem !important;
    }
    header[data-testid="stHeader"] {
        background: transparent;
        display: none;
    }
    
    @keyframes piscar {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    .alerta-piscar {
        color: #ff4b4b;
        font-size: 26px;
        font-weight: bold;
        animation: piscar 1s infinite;
    }
    .alerta-sub {
        color: #ff6b6b;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 12px;
    }
    .alerta-comparacao {
        background-color: #2c1515;
        border-left: 4px solid #ff4b4b;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 14px;
        color: #ffffff;
        margin-bottom: 12px;
        margin-top: 5px;
    }
    
    .card-pedido {
        background-color: #1e1e1e;
        border: 2px solid #f1c40f;
        padding: 10px;
        border-radius: 6px;
        font-size: 13px;
        color: #ffffff;
        margin-bottom: 8px;
        text-align: left;
        line-height: 1.4;
    }
    .card-pedido-prioridade {
        background-color: #2b1616;
        border: 2px solid #ff4b4b;
        padding: 10px;
        border-radius: 6px;
        font-size: 13px;
        color: #ffffff;
        margin-bottom: 8px;
        text-align: left;
        line-height: 1.4;
        box-shadow: 0 0 8px rgba(255, 75, 75, 0.6);
    }
    .texto-destaque-lpn {
        font-size: 20px !important;
        font-weight: bold;
        color: #2ecc71;
    }
    .texto-destaque-mat {
        font-size: 18px !important;
        font-weight: bold;
        color: #f1c40f;
    }
    
    .box-pergunta-container {
        background-color: #1a1a1a;
        border: 1px solid #444;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 15px;
    }

    /* Estilo preciso para o botão de Validar LPN (Retangular deitado igual ao seu modelo) */
    div.stButton > button[kind="secondary"].botao-validar-custom {
        background-color: #1b2421 !important;
        border: 2px solid #52b788 !important;
        color: #52b788 !important;
        border-radius: 12px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        height: 110px !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(82, 183, 136, 0.3) !important;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button[kind="secondary"].botao-validar-custom:hover {
        background-color: #2d6a4f !important;
        color: #ffffff !important;
        border-color: #74c69d !important;
    }
    </style>
""", unsafe_allow_html=True)
