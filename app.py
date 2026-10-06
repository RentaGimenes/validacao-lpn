# ==========================================
# IMPORTAÇÕES DE BIBLIOTECAS
# ==========================================
import base64
from datetime import datetime, timedelta
import os
import re
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import pytz
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Configura a página do Streamlit para usar layout largo
st.set_page_config(page_title="Validação de Lpn", page_icon="📦", layout="wide")

# ==========================================
# MAPEAMENTO DE IMAGENS E ARQUIVOS
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

# Atualiza a página automaticamente a cada 3 minutos
count = st_autorefresh(interval=180000, key="datarefresh")

# ==========================================
# ESTILOS VISUAIS (CSS CUSTOMIZADO)
# ==========================================
st.markdown(
    """
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
    
    .card-pedido {
        background-color: #262211;
        border: 1px solid #d4ac0d;
        padding: 10px;
        border-radius: 6px;
        font-size: 13px;
        color: #ffffff;
        margin-bottom: 8px;
        text-align: left;
        line-height: 1.4;
        cursor: pointer;
        transition: 0.2s;
    }
    .card-pedido:hover {
        border-color: #00bfff;
    }
    .card-pedido-prioridade {
        background-color: #2b1616;
        border: 1px solid #ff4b4b;
        padding: 10px;
        border-radius: 6px;
        font-size: 13px;
        color: #ffffff;
        margin-bottom: 8px;
        text-align: left;
        line-height: 1.4;
    }
    
    .card-pedido-concluido {
        background-color: #112615;
        border: 1px solid #2ecc71;
        padding: 10px;
        border-radius: 6px;
        font-size: 13px;
        color: #ffffff;
        margin-bottom: 8px;
        text-align: left;
        line-height: 1.4;
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

    /* Alinhamento da coluna do meio e centralização perfeita do botão */
    .container-coluna-meio {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        text-align: center;
        min-height: 380px;
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
        max-width: 320px !important;
        display: flex !important;
        justify-content: center !important;
        margin: 0 auto !important;
    }
    
    div.stButton > button {
        background: rgba(0, 255, 100, 0.15) !important;
        border: 2px solid #00ff66 !important;
        border-radius: 8px !important;
        box-shadow: 0 0 12px rgba(0, 255, 100, 0.6), inset 0 0 8px rgba(0, 255, 100, 0.4) !important;
        color: #00ff66 !important;
        font-weight: bold !important;
        font-size: 15px !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
        height: 75px !important;
        text-align: center !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 20px rgba(0, 255, 100, 0.9), inset 0 0 12px rgba(0, 255, 100, 0.6) !important;
        background: rgba(0, 255, 100, 0.25) !important;
        border-color: #00ff88 !important;
        color: #ffffff !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Função para tocar som de erro
def tocar_som_erro():
  sound_html = """
        <audio autoplay>
            <source src="https://assets.mixkit.co/active_storage/sfx/2575/2575-preview.mp3" type="audio/mpeg">
        </audio>
    """
  st.markdown(sound_html, unsafe_allow_html=True)


# Conexão com a planilha do Google Sheets
def init_connection():
  scope = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]
  creds_dict = dict(st.secrets["gcp_service_account"])
  if "private_key" in creds_dict:
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
  creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
  client = gspread.authorize(creds)
  return client


@st.cache_data(ttl=30)
def carregar_dados_planilha():
  client = init_connection()
  spreadsheet_name = "SOLICITAÇÃO DE LPN"
  sheet = client.open(spreadsheet_name).worksheet("SOLICITAÇÕES")
  registos = sheet.get_all_values()
  return sheet, registos


# Carrega os dados com tratamento de erro
try:
  with st.spinner("Conectando ao Google Sheets e carregando dados..."):
    sheet, registos = carregar_dados_planilha()
  dados_validos = []
  if len(registos) > 1:
    for r in registos[1:]:
      if any(str(celula).strip() for celula in r):
        dados_validos.append(r)
except Exception as e:
  st.error(f"Erro ao conectar com o Google Sheets: {e}")
  st.stop()


# ==========================================
# FUNÇÕES DE APOIO E TRATAMENTO DE TEXTO
# ==========================================
def limpar_texto(texto):
  if not texto:
    return ""
  return (
      str(texto)
      .replace(".", "")
      .replace("/", "")
      .replace("-", "")
      .replace(" ", "")
      .strip()
  )


def extrair_hora_da_string(texto_coluna):
  if not texto_coluna:
    return ""
  texto_str = str(texto_coluna).strip()
  match_hora = re.search(r"(\d{2}:\d{2}(?::\d{2})?)", texto_str)
  if match_hora:
    return match_hora.group(1)
  return texto_str


def obter_tres_primeiras_palavras(descricao):
  if not descricao:
    return ""
  palavras = str(descricao).split()
  return " ".join(palavras[:3])


def formatar_lote_rigoroso(lote_str):
  if not lote_str:
    return ""
  digitos = re.sub(r"\D", "", str(lote_str))
  if not digitos:
    return ""
  miolo = digitos[-7:] if len(digitos) >= 7 else digitos.zfill(7)
  return "0000000" + miolo


def formatar_lote_lido_rigoroso(lote_str):
  if not lote_str:
    return ""
  digitos = re.sub(r"\D", "", str(lote_str))
  if not digitos:
    return ""
  miolo_lote = digitos[-7:] if len(digitos) >= 7 else digitos.zfill(7)
  return "0000000" + miolo_lote


def converter_para_data_obj(data_str):
  if not data_str:
    return None
  data_str = str(data_str).strip()
  if re.match(r"^\d{4}-\d{2}-\d{2}$", data_str):
    try:
      return datetime.strptime(data_str, "%Y-%m-%d").date()
    except Exception:
      pass
  if re.match(r"^\d{2}\.\d{2}\.\d{2}$", data_str):
    try:
      partes = data_str.split(".")
      return datetime(
          int("20" + partes[0]), int(partes[1]), int(partes[2])
      ).date()
    except Exception:
      pass
  if len(data_str) == 6 and data_str.isdigit():
    try:
      return datetime(
          int("20" + data_str[0:2]), int(data_str[2:4]), int(data_str[4:6])
      ).date()
    except Exception:
      pass
  digitos = re.sub(r"\D", "", data_str)
  for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d", "%Y/%m/%d", "%d%m%Y"):
    try:
      return datetime.strptime(data_str, fmt).date()
    except Exception:
      continue
  if len(digitos) == 8:
    try:
      return datetime(
          int(digitos[4:8]), int(digitos[2:4]), int(digitos[0:2])
      ).date()
    except Exception:
      pass
  return None


def formatar_para_aammdd(data_str):
  if not data_str:
    return ""
  data_obj = converter_para_data_obj(str(data_str))
  if data_obj:
    return data_obj.strftime("%y%m%d")
  digitos = re.sub(r"\D", "", str(data_str))
  if len(digitos) == 6:
    return digitos
  return str(data_str)


def processar_codigo_1(barcode):
  return barcode.replace("(", "").replace(")", "").strip()


def processar_codigo_2(barcode):
  try:
    limpo = barcode.replace("(", "").replace(")", "")
    match_mat = re.search(r"90(\d+?)(?=37|$)", limpo)
    mat = match_mat.group(1) if match_mat else limpo[2:10]
    match_qtd = re.search(r"37(\d+)", limpo)
    quantidade = (
        int(match_qtd.group(1).lstrip("0") or "0") if match_qtd else 0
    )

    lote = ""
    digitos_lote = re.sub(r"\D", "", limpo)
    if len(digitos_lote) >= 13:
      lote = digitos_lote[-13:-6]
    else:
      parts = limpo.split()
      if len(parts) > 1:
        lote = parts[-1]

    return limpar_texto(mat), quantidade, lote
  except Exception:
    return "", 0, ""


def processar_codigo_3(barcode):
  try:
    limpo = barcode.replace("(", "").replace(")", "")
    match_dun = re.search(r"(?:^|\D)02(\d{14})", limpo)
    dun = (
        match_dun.group(1)
        if match_dun
        else (
            re.search(r"02(\d+?)(?=17|11|$)", limpo).group(1)
            if re.search(r"02(\d+?)(?=17|11|$)", limpo)
            else limpo[2:16]
        )
    )
    match_venc = re.search(r"17(\d{6})", limpo)
    vencimento = match_venc.group(1) if match_venc else ""
    matches_fab = re.findall(r"11(\d{6})", limpo)
    fabricacao = matches_fab[-1] if matches_fab else ""
    return limpar_texto(dun), limpar_texto(vencimento), limpar_texto(fabricacao)
  except Exception:
    return "", "", ""


def obter_quantidade_inteira(r):
  try:
    return (
        int(re.sub(r"\D", "", str(r[4])))
        if len(r) > 4 and str(r[4]).strip()
        else 0
    )
  except Exception:
    return 0


def obter_lista_quebras(r):
  try:
    texto_quebras = str(r[6]).strip() if len(r) > 6 else ""
    if not texto_quebras or texto_quebras == "0":
      return []
    return [
        int(re.sub(r"\D", "", p))
        for p in texto_quebras.split(",")
        if p.strip() and re.sub
