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
    page_title="Validação das Informações das Lpn",
    layout="wide"
)

# ==========================================
# INICIALIZAÇÃO DE VARIÁVEIS DE ESTADO
# ==========================================
if "pedido_selecionado" not in st.session_state:
    st.session_state.pedido_selecionado = False

# ==========================================
# TÍTULO PRINCIPAL
# ==========================================
st.title("📦 Validação das Informações das Lpn")
st.subheader("Painel de Solicitações Pendentes e Validação")

st.markdown("### Selecione o pedido abaixo para iniciar:")

# ==========================================
# SEÇÃO DO PEDIDO PENDENTE (EXEMPLO)
# ==========================================
col_pedido, _ = st.columns([1, 2])

with col_pedido:
    # Caixa simulando o card do pedido
    st.markdown("""
        <div style='border: 1px solid #ffcc00; padding: 10px; border-radius: 5px; background-color: #1e1e1e;'>
            <b>Linha:</b> R03<br>
            <b>Cód Mat:</b> 65684949<br>
            <b>Desc:</b> DOVE SH NUTRI+TRI-OLEO...<br>
            <b>Data Palete:</b> 26.09.09<br>
            <b>Venc:</b> 08/09/2029<br>
            <b>Lote:</b> 2026252<br>
            <b>LPN Inteira:</b> 1<br>
            <b>Quebra:</b> 0<br><br>
            <span style='color: #ffcc00;'><b>Progresso:</b> 0/1 (0%)</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Botão para selecionar o pedido
    if st.button("Selecionar Pedido 1"):
        st.session_state.pedido_selecionado = True
        st.success("Pedido selecionado com sucesso!")

st.markdown("---")

# ==========================================
# SEÇÃO DE VALIDAÇÃO E BAIXA NA LPN
# ==========================================
st.subheader("📝 Validar e Dar Baixa na LPN")

# Dividindo a tela em duas colunas: Formulário à esquerda e Etiqueta/Botão à direita
col_form, col_etiqueta = st.columns([1, 1])

with col_form:
    # Campo para digitar o nome do operador
    nome = st.text_input("Nome", placeholder="Digite seu nome...")
    
    # Aviso caso nenhum pedido esteja selecionado
    if not st.session_state.pedido_selecionado:
        st.markdown(
            "<div style='padding: 8px; background-color: #511; color: #ff9999; border: 1px solid #aa3333; text-align: center; border-radius: 4px;'>"
            "⚠️ POR FAVOR, SELECIONE UM PEDIDO PARA CONFIRMAR AS LPN"
            "</div>", 
            unsafe_allow_html=True
        )
    
    # Campos de código de barras
    cb1 = st.text_input("1º Código de Barras (LPN)")
    cb2 = st.text_input("2º Código de Barras")
    cb3 = st.text_input("3º Código de Barras")

with col_etiqueta:
    # Exibição simulada do layout da etiqueta (substitua pela sua imagem ou componente real)
    st.markdown("""
        <div style='border: 2px solid #ccc; padding: 15px; border-radius: 8px; background-color: #fff; color: #000; text-align: center;'>
            <b>XX(SKU DA SUA LPN AQUI)XX</b><br><br>
            <div style='font-size: 12px; text-align: left;'>
                <b>MATERIAL:</b> SU DO SEU MATERIAL<br>
                <b>DESCRIÇÃO:</b> NOME DO SEU MATERIAL<br>
                <b>ORDEM DE PRODUÇÃO:</b> 000009908984/R03<br>
                <b>LOTE:</b> 0000002026252160001
            </div>
            <hr style='border: 1px dashed #000;'>
            <p style='font-family: monospace; font-size: 18px;'>|||||||||||||||||||||||||||||||||||</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") # Espaçamento
    
    # BOTÃO DE VALIDAÇÃO GARANTIDO NA TELA
    # Habilitado apenas se o pedido estiver selecionado e o nome preenchido
    botao_liberado = st.session_state.pedido_selecionado and bool(nome.strip())
    
    if st.button("VALIDAR LPN", use_container_width=True, disabled=not botao_liberado):
        if not st.session_state.pedido_selecionado:
            st.error("Selecione um pedido antes de validar.")
        elif not nome.strip():
            st.warning("Por favor, digite seu nome antes de validar.")
        else:
            # Lógica de salvamento / baixa bem-sucedida
            st.success("LPN validada e baixa realizada com sucesso!")
