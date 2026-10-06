# ==========================================
# IMPORTAÇÃO DAS BIBLIOTECAS NECESSÁRIAS
# ==========================================
from datetime import datetime, timedelta
import os
import re
import base64
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import pytz
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Configurando a página para usar o layout largo
st.set_page_config(page_title="Validação de Lpn", page_icon="📦", layout="wide")

# ==========================================
# MAPEAMENTO DOS ARQUIVOS E IMAGENS
# ==========================================
IMAGENS = {
    "guia05": "GUIA DE CODIGO DE LPN.JPG",
    "conf_desc": "descricao material.png",
    "conf_ordem": "ordemdeprod.png",
    "material04": "ERRO NO MATERIAL - INCOMPATIVEL COM O SOLICITADO.png",
    "lote06": "LOTE IMCOMPATIVEL COM A DATA DE VENCIMENTO.png",
    "datav02": "DATA DE VENCIMENTO NAO ESTA COMPATIVEL.png",
    "datafab03": "DATA DE FABRICAÇÃO NAO ESTA DE ACORDO COM O SOLICITADO.png",
    "dun03": "DUN NAO ESTA CORRESPONDENTE A DUN DO MATERIAL SOLICITADO.png",
    "validacao_qtd": "validação da quantidade.PNG",
    "lpn_duplicada": "lpnduplicada.PNG",
    "sonic_gif": "SONICGIF.gif",
    "att_gif": "att.gif",
    "validar_btn": "validar.png",
}

# Atualiza a tela a cada 3 minutos automaticamente
count = st_autorefresh(interval=180000, key="datarefresh")

# ==========================================
# ESTILOS E CUSTOMIZAÇÃO (CSS)
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
        font-size: 24px;
        font-weight: bold;
        animation: piscar 1s infinite;
        text-align: center;
        width: 100%;
    }
    .alerta-sub {
        color: #ff6b6b;
        font-size: 15px;
        font-weight: bold;
        margin-bottom: 10px;
        text-align: center;
        width: 100%;
    }
    .alerta-comparacao {
        background-color: #2c1515;
        border-left: 4px solid #ff4b4b;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 13px;
        color: #ffffff;
        margin-bottom: 10px;
        margin-top: 5px;
        text-align: left;
        width: 100%;
        box-sizing: border-box;
    }
    
    /* Cartões compactos e quadradinhos */
    .card-pedido {
        background-color: #262211;
        border: 1px solid #d4ac0d;
        padding: 6px 8px;
        border-radius: 6px;
        font-size: 11px;
        color: #ffffff;
        margin-bottom: 6px;
        text-align: left;
        line-height: 1.25;
        cursor: pointer;
        transition: 0.2s;
    }
    .card-pedido:hover {
        border-color: #00bfff;
    }
    .card-pedido-prioridade {
        background-color: #2b1616;
        border: 1px solid #ff4b4b;
        padding: 6px 8px;
        border-radius: 6px;
        font-size: 11px;
        color: #ffffff;
        margin-bottom: 6px;
        text-align: left;
        line-height: 1.25;
    }
    
    .card-pedido-concluido {
        background-color: #112615;
        border: 1px solid #2ecc71;
        padding: 6px 8px;
        border-radius: 6px;
        font-size: 11px;
        color: #ffffff;
        margin-bottom: 6px;
        text-align: left;
        line-height: 1.25;
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

    .container-coluna-meio {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        width: 100%;
        text-align: center;
        margin-top: -10px;
    }
    .container-coluna-meio img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    
    .container-botao-centralizado {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin: 0 auto;
    }
    .container-botao-centralizado div.stButton {
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
    }
    
    div.stButton > button {
        background: rgba(0, 255, 100, 0.15) !important;
        border: 2px solid #00ff66 !important;
        border-radius: 8px !important;
        box-shadow: 0 0 12px rgba(0, 255, 100, 0.6), inset 0 0
