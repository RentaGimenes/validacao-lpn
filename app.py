# ==========================================
# IMPORTAÇÕES DE BIBLIOTECAS
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

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    layout="wide", 
    page_title="Validar e Dar Baixa na LPN"
)

# ==========================================
# CSS PERSONALIZADO (Botão Verde e Estilos)
# ==========================================
st.markdown("""
    <style>
        /* Estiliza o botão de validação para verde vibrante */
        div.stButton > button:first-child {
            background-color: #28a745;
            color: white;
            font-size: 18px;
            font-weight: bold;
            height: 55px;
            width: 100%;
            border-radius: 8px;
            border: none;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
            transition: 0.3s;
        }
        div.stButton > button:first-child:hover {
            background-color: #218838;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# FUNÇÕES DE APOIO E CONEXÃO
# ==========================================
@st.cache_resource
def obter_fuso_horario():
    return pytz.timezone('America/Sao_Paulo')

pytz_sp = obter_fuso_horario()

def conectar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
            client = gspread.authorize(creds)
            return client
    except Exception as e:
        pass
    return None

# ==========================================
# TÍTULO PRINCIPAL
# ==========================================
st.markdown("<h2>📝 Validar e Dar Baixa na LPN</h2>", unsafe_allow_html=True)
st.write("")

# ==========================================
# LAYOUT EM COLUNAS
# ==========================================
col_inputs, col_lpn, col_action = st.columns([1.2, 1.2, 1.3], gap="large")

with col_inputs:
    st.subheader("Entrada de Dados")
    nome = st.text_input("Nome", placeholder="Digite seu nome...")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    lpn_1 = st.text_input("1º Código de Barras (LPN)")
    lpn_2 = st.text_input("2º Código de Barras")
    lpn_3 = st.text_input("3º Código de Barras")

with col_lpn:
    # Espaçamento para alinhar perfeitamente com o topo dos inputs de código de barras
    st.markdown("<div style='height: 55px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🏷️ Modelo de LPN")
    
    # Exibe a imagem de modelo da LPN alinhada ao lado dos códigos de barras
    try:
        st.image("image_51919d.png", caption="Exemplo de Etiqueta LPN", use_container_width=True)
    except:
        st.info("Coloque a imagem 'image_51919d.png' na mesma pasta do script para exibi-la aqui.")

with col_action:
    # Alinhamento vertical com o topo
    st.markdown("<div style='height: 55px;'></div>", unsafe_allow_html=True)
    
    # Alerta de seleção de pedido
    st.markdown("""
        <div style="background-color: rgba(220, 53, 69, 0.15); border: 1px solid #dc3545; padding: 12px; border-radius: 6px; text-align: center; margin-bottom: 25px;">
            <span style="color: #ff6b6b; font-weight: bold; font-size: 14px;">⚠️ POR FAVOR, SELECIONE UM PEDIDO PARA CONFIRMAR AS LPN</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # O BOTÃO VERDE
    if st.button("🟢 VALIDAR LPN"):
        if not nome:
            st.error("Por favor, preencha o seu nome antes de validar!")
        elif not lpn_1:
            st.error("O 1º Código de Barras (LPN) é obrigatório!")
        else:
            agora = datetime.now(pytz_sp).strftime('%d/%m/%Y %H:%M:%S')
            st.success(f"LPN validada com sucesso por {nome} em {agora}!")
