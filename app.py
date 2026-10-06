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

# Configurando a página para usar a tela inteira
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

# Atualiza a página sozinho a cada 3 minutos
count = st_autorefresh(interval=180000, key="datarefresh")

# ==========================================
# ESTILOS VISUAIS (CSS) - CARTÕES MENORES E QUADRADOS
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
    
    /* Cartões compactos e mais quadrados */
    .card-pedido {
        background-color: #262211;
        border: 1px solid #d4ac0d;
        padding: 6px 8px;
        border-radius: 5px;
        font-size: 11px;
        color: #ffffff;
        margin-bottom: 6px;
        text-align: left;
        line-height: 1.25;
        height: 185px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .card-pedido:hover {
        border-color: #00bfff;
    }
    
    .card-pedido-prioridade {
        background-color: #2b1616;
        border: 1px solid #ff4b4b;
        padding: 6px 8px;
        border-radius: 5px;
        font-size: 11px;
        color: #ffffff;
        margin-bottom: 6px;
        text-align: left;
        line-height: 1.25;
        height: 185px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .card-pedido-concluido {
        background-color: #112615;
        border: 1px solid #2ecc71;
        padding: 6px 8px;
        border-radius: 5px;
        font-size: 11px;
        color: #ffffff;
        margin-bottom: 6px;
        text-align: left;
        line-height: 1.25;
        height: 170px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
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
    }
    div.stButton > button:hover {
        box-shadow: 0 0 20px rgba(0, 255, 100, 0.9), inset 0 0 12px rgba(0, 255, 100, 0.6) !important;
        background: rgba(0, 255, 100, 0.25) !important;
        border-color: #00ff88 !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# Toca um som curto se der erro
def tocar_som_erro():
    sound_html = """
        <audio autoplay>
            <source src="https://assets.mixkit.co/active_storage/sfx/2575/2575-preview.mp3" type="audio/mpeg">
        </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# Ligo aqui com a planilha do Google Sheets usando os secrets
def init_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
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

try:
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
# FUNÇÕES DE TRATAMENTO DOS DADOS
# ==========================================
def limpar_texto(texto):
    if not texto: return ""
    return str(texto).replace(".", "").replace("/", "").replace("-", "").replace(" ", "").strip()

def extrair_hora_da_string(texto_coluna):
    if not texto_coluna: return ""
    texto_str = str(texto_coluna).strip()
    match_hora = re.search(r'(\d{2}:\d{2}(?::\d{2})?)', texto_str)
    if match_hora:
        return match_hora.group(1)
    return texto_str

def formatar_lote_rigoroso(lote_str):
    if not lote_str: return ""
    digitos = re.sub(r'\D', '', str(lote_str))
    if not digitos:
        return ""
    miolo = digitos[-7:] if len(digitos) >= 7 else digitos.zfill(7)
    return "0000000" + miolo

def formatar_lote_lido_rigoroso(lote_str):
    if not lote_str: return ""
    digitos = re.sub(r'\D', '', str(lote_str))
    if not digitos:
        return ""
    miolo_lote = digitos[-7:] if len(digitos) >= 7 else digitos.zfill(7)
    return "0000000" + miolo_lote

def converter_para_data_obj(data_str):
    if not data_str: return None
    data_str = str(data_str).strip()
    if re.match(r'^\d{4}-\d{2}-\d{2}$', data_str):
        try: return datetime.strptime(data_str, "%Y-%m-%d").date()
        except Exception: pass
    if re.match(r'^\d{2}\.\d{2}\.\d{2}$', data_str):
        try:
            partes = data_str.split('.')
            return datetime(int("20" + partes[0]), int(partes[1]), int(partes[2])).date()
        except Exception: pass
    if len(data_str) == 6 and data_str.isdigit():
        try:
            return datetime(int("20" + data_str[0:2]), int(data_str[2:4]), int(data_str[4:6])).date()
        except Exception: pass
    digitos = re.sub(r'\D', '', data_str)
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d", "%Y/%m/%d", "%d%m%Y"):
        try: return datetime.strptime(data_str, fmt).date()
        except Exception: continue
    if len(digitos) == 8:
        try: return datetime(int(digitos[4:8]), int(digitos[2:4]), int(digitos[0:2])).date()
        except Exception: pass
    return None

def formatar_para_aammdd(data_str):
    if not data_str:
        return ""
    data_obj = converter_para_data_obj(str(data_str))
    if data_obj:
        return data_obj.strftime("%y%m%d")
    digitos = re.sub(r'\D', '', str(data_str))
    if len(digitos) == 6:
        return digitos
    return str(data_str)

def processar_codigo_1(barcode):
    return barcode.replace("(", "").replace(")", "").strip()

def processar_codigo_2(barcode):
    try:
        limpo = barcode.replace("(", "").replace(")", "")
        match_mat = re.search(r'90(\d+?)(?=37|$)', limpo)
        mat = match_mat.group(1) if match_mat else limpo[2:10]
        match_qtd = re.search(r'37(\d+)', limpo)
        quantidade = int(match_qtd.group(1).lstrip('0') or '0') if match_qtd else 0
        
        lote = ""
        digitos_lote = re.sub(r'\D', '', limpo)
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
        match_dun = re.search(r'(?:^|\D)02(\d{14})', limpo)
        dun = match_dun.group(1) if match_dun else (re.search(r'02(\d+?)(?=17|11|$)', limpo).group(1) if re.search(r'02(\d+?)(?=17\vert{}11\vert{}$)', limpo) else limpo[2:16])
        match_venc = re.search(r'17(\d{6})', limpo)
        vencimento = match_venc.group(1) if match_venc else ""
        matches_fab = re.findall(r'11(\d{6})', limpo)
        fabricacao = matches_fab[-1] if matches_fab else ""
        return limpar_texto(dun), limpar_texto(vencimento), limpar_texto(fabricacao)
    except Exception:
        return "", "", ""

def obter_quantidade_inteira(r):
    try:
        return int(re.sub(r'\D', '', str(r[4]))) if len(r) > 4 and str(r[4]).strip() else 0
    except Exception:
        return 0

def obter_lista_quebras(r):
    try:
        texto_quebras = str(r[6]).strip() if len(r) > 6 else ""
        if not texto_quebras or texto_quebras == "0": return []
        return [int(re.sub(r'\D', '', p)) for p in texto_quebras.split(',') if p.strip() and re.sub(r'\D', '', p).isdigit()]
    except Exception:
        return []

def obter_quantidade_total_lpns(r):
    total = obter_quantidade_inteira(r) + len(obter_lista_quebras(r))
    return total if total > 0 else 1

# ==========================================
# TÍTULO E VARIÁVEIS DE SESSÃO
# ==========================================
st.markdown("<h2 style='margin-top: 0px; padding-top: 0px;'>📦 Validação das informações das Lpn</h2>", unsafe_allow_html=True)

if "etapa_validacao" not in st.session_state:
    st.session_state.etapa_validacao = False
    st.session_state.dados_conferencia = {}
if "lpns_validadas_por_pedido" not in st.session_state:
    st.session_state.lpns_validadas_por_pedido = {}
if "erro_ativo" not in st.session_state:
    st.session_state.erro_ativo = None
if "detalhes_erro" not in st.session_state:
    st.session_state.detalhes_erro = {"solicitado": "", "lido": ""}
if "pedido_selecionado_idx" not in st.session_state:
    st.session_state.pedido_selecionado_idx = None
if "val_nome" not in st.session_state: st.session_state.val_nome = ""
if "val_bc1" not in st.session_state: st.session_state.val_bc1 = ""
if "val_bc2" not in st.session_state: st.session_state.val_bc2 = ""
if "val_bc3" not in st.session_state: st.session_state.val_bc3 = ""

# ==========================================
# TELA 1: CONFIRMAÇÃO VISUAL
# ==========================================
if st.session_state.etapa_validacao:
    st.subheader("🔍 Confirmação Visual Obrigatória")
    d = st.session_state.dados_conferencia
    st.success(f"✔ Validando LPN para o **Pedido {d['num_pedido']}**!")
    
    sonic_path = IMAGENS["sonic_gif"]
    sonic_html = ""
    if os.path.exists(sonic_path):
        with open(sonic_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            sonic_html = f'<img src="data:image/gif;base64,{encoded}" width="75px" style="vertical-align: middle; margin-left: 15px;">'
    
    st.markdown(f"""
    <div style="background-color: #000000; border: 2px solid #f1c40f; padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; display: inline-flex; align-items: center; max-width: 100%;">
        <div style="color: #f1c40f; font-size: 14px; font-weight: bold; line-height: 1.4;">
            ⚠ LPNs MERAMENTE ILUSTRATIVAS<br>
            SEUS VALORES DEVEM SER CONSIDERADOS APENAS COMO EXEMPLO PARA FACILITAR A VISUALIZAÇÃO DA DIVERGÊNCIA.
        </div>
        {sonic_html}
    </div>
    """, unsafe_allow_html=True)
    
    # Linha corrigida sem erro de f-string
    st.markdown(f'📦 **LPN Atual:** <span class="texto-destaque-lpn">{d["lpn"]}</span>', unsafe_allow_html=True)
    st.markdown(f'🏷 **Material:** <span class="texto-destaque-mat">{d["descricao"]}</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_conf1, col_centro, col_conf2 = st.columns([2, 1.5, 2], gap="medium")
    
    with col_conf1:
        st.markdown("📌 **A descrição está correta?**")
        resp_desc = st.radio("A descrição está correta?", ["Sim", "Não"], key="resp_desc_val", horizontal=True, label_visibility="collapsed", index=None)
        st.markdown("<br>", unsafe_allow_html=True)
        if os.path.exists(IMAGENS["conf_desc"]): 
            st.image(IMAGENS["conf_desc"], width=420)
        
    with col_conf2:
        st.markdown("📌 **Você verificou a ordem?**")
        resp_ordem = st.radio("Você verificou a ordem?", ["Sim", "Não"], key="resp_ordem_val", horizontal=True, label_visibility="collapsed", index=None)
        st.markdown("<br>", unsafe_allow_html=True)
        if os.path.exists(IMAGENS["conf_ordem"]): 
            st.image(IMAGENS["conf_ordem"], width=420)
