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
# CONFIGURAÇÃO DE IMAGENS E ARQUIVOS
# ==========================================
# (Adicione suas configurações iniciais aqui se precisar)

# Configuração da página do app
st.set_page_config(page_title="Validação de Pedidos", layout="centered")

# CSS personalizado para criar o retângulo escuro e jogar o Sim/Não lá dentro alinhado
st.markdown("""
    <style>
    .caixa-pergunta {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 12px 15px;
        margin-bottom: 15px;
    }
    .titulo-pergunta {
        color: #ffffff;
        font-weight: 500;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.subheader("Painel de Verificação")

# ==========================================
# PERGUNTAS DO SISTEMA
# ==========================================

# Bloco 1: A descrição está correta?
st.markdown('<div class="caixa-pergunta"><div class="titulo-pergunta">📌 A descrição está correta?</div>', unsafe_allow_html=True)
desc_correta = st.radio(
    "A descrição está correta?", 
    ["Sim", "Não"], 
    key="desc_correta", 
    horizontal=True, 
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)


# Bloco 2: Você verificou a ordem?
st.markdown('<div class="caixa-pergunta"><div class="titulo-pergunta">📌 Você verificou a ordem?</div>', unsafe_allow_html=True)
ordem_verificada = st.radio(
    "Você verificou a ordem?", 
    ["Sim", "Não"], 
    key="ordem_verificada", 
    horizontal=True, 
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)


# Botão de salvar/enviar dados
if st.button("Salvar Respostas"):
    # Só um print simples pras respostas
    st.success(f"Respostas salvas! Descrição correta: {desc_correta} | Ordem verificada: {ordem_verificada}")
