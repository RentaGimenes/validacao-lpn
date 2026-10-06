# ==========================================
# IMPORTAÇÕES NECESSÁRIAS
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

# Configuro a página para usar a largura inteira
st.set_page_config(page_title="Validação de Lpn", page_icon="📦", layout="wide")

# ==========================================
# MAPEAMENTO DOS ARQUIVOS DE IMAGEM
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

# Atualizo a tela automaticamente a cada 3 minutos
count = st_autorefresh(interval=180000, key="datarefresh")

# ==========================================
# ESTILOS VISUAIS (CSS) - CARTÕES MAIS QUADRADOS
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
    
    /* Cartões dos pedidos mais quadrados e compactos */
    .card-pedido {
        background-color: #262211;
        border: 1px solid #d4ac0d;
        padding: 5px 6px;
        border-radius: 5px;
        font-size: 10px;
        color: #ffffff;
        margin-bottom: 4px;
        text-align: left;
        line-height: 1.2;
        height: 145px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .card-pedido:hover
