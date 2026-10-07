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

    /* Alinhamento e centralização perfeita da coluna do meio */
    .container-coluna-meio {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        width: 100%;
        text-align: center;
        margin-top: 0px;
    }
    
    .container-botao-centralizado {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin: 15px auto 0 auto;
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

    /* Centralização estrita da coluna da direita */
    .container-coluna-direita {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        width: 100%;
        text-align: center;
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
        if p.strip() and re.sub(r"\D", "", p).isdigit()
    ]
  except Exception:
    return []


def obter_quantidade_total_lpns(r):
  total = obter_quantidade_inteira(r) + len(obter_lista_quebras(r))
  return total if total > 0 else 1


# ==========================================
# CABEÇALHO DO APLICATIVO
# ==========================================
st.markdown(
    "<h2 style='margin-top: 0px; padding-top: 0px;'>📦 Validação das"
    " informações das Lpn</h2>",
    unsafe_allow_html=True,
)

# Inicialização dos estados da sessão
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
if "val_nome" not in st.session_state:
  st.session_state.val_nome = ""
if "val_bc1" not in st.session_state:
  st.session_state.val_bc1 = ""
if "val_bc2" not in st.session_state:
  st.session_state.val_bc2 = ""
if "val_bc3" not in st.session_state:
  st.session_state.val_bc3 = ""

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

  st.markdown(
      f"""
    <div style="background-color: #000000; border: 2px solid #f1c40f; padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; display: inline-flex; align-items: center; max-width: 100%;">
        <div style="color: #f1c40f; font-size: 14px; font-weight: bold; line-height: 1.4;">
            ⚠ LPNs MERAMENTE ILUSTRATIVAS<br>
            SEUS VALORES DEVEM SER CONSIDERADOS APENAS COMO EXEMPLO PARA FACILITAR A VISUALIZAÇÃO DA DIVERGÊNCIA.
        </div>
        {sonic_html}
    </div>
    """,
      unsafe_allow_html=True,
  )

  st.markdown(
      f'📦 **LPN Atual:** <span class="texto-destaque-lpn">{d["lpn"]}</span>',
      unsafe_allow_html=True,
  )
  st.markdown(
      f'🏷 **Material:** <span class="texto-destaque-mat">{d["descricao"]}</span>',
      unsafe_allow_html=True,
  )
  st.markdown("<br>", unsafe_allow_html=True)

  col_conf1, col_centro, col_conf2 = st.columns([2, 1.5, 2], gap="medium")

  with col_conf1:
    st.markdown("📌 **A descrição está correta?**")
    resp_desc = st.radio(
        "A descrição está correta?",
        ["Sim", "Não"],
        key="resp_desc_val",
        horizontal=True,
        label_visibility="collapsed",
        index=None,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists(IMAGENS["conf_desc"]):
      st.image(IMAGENS["conf_desc"], width=420)

  with col_conf2:
    st.markdown("📌 **Você verificou a ordem?**")
    resp_ordem = st.radio(
        "Você verificou a ordem?",
        ["Sim", "Não"],
        key="resp_ordem_val",
        horizontal=True,
        label_visibility="collapsed",
        index=None,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists(IMAGENS["conf_ordem"]):
      st.image(IMAGENS["conf_ordem"], width=420)

  with col_centro:
    st.markdown("<br><br><br>", unsafe_allow_html=True)

    num_ped_atual = d["num_pedido"]
    lpns_ja_lidas_atual = st.session_state.lpns_validadas_por_pedido.get(
        num_ped_atual, []
    )
    total_nec_atual = d["total_esperado"]

    if (len(lpns_ja_lidas_atual) + 1) < total_nec_atual:
      texto_botao_confirmar = "✔ Validar\npróxima LPN"
    else:
      texto_botao_confirmar = "✔ Confirmar\nesta LPN"

    if st.button(texto_botao_confirmar, key="btn_confirmar_etapa_visual"):
      if resp_ordem == "Sim" and resp_desc == "Sim":
        try:
          linha = d["linha"]
          num_ped = d["num_pedido"]
          lpn_atual = d["lpn"]
          responsavel_acao = d["responsavel"]
          total_necessario = d["total_esperado"]

          if num_ped not in st.session_state.lpns_validadas_por_pedido:
            st.session_state.lpns_validadas_por_pedido[num_ped] = []
          if lpn_atual not in st.session_state.lpns_validadas_por_pedido[num_ped]:
            st.session_state.lpns_validadas_por_pedido[num_ped].append(lpn_atual)

          lpns_lidas_pedido = st.session_state.lpns_validadas_por_pedido[
              num_ped
          ]
          if len(lpns_lidas_pedido) >= total_necessario:
            fuso_horario = pytz.timezone("America/Sao_Paulo")
            hora_atual = datetime.now(fuso_horario).strftime("%d/%m/%Y %H:%M:%S")
            todas_lpns_str = ", ".join(lpns_lidas_pedido)

            sheet.update_cell(linha, 12, responsavel_acao)
            sheet.update_cell(linha, 13, todas_lpns_str)
            sheet.update_cell(linha, 14, hora_atual)

            if num_ped in st.session_state.lpns_validadas_por_pedido:
              del st.session_state.lpns_validadas_por_pedido[num_ped]
            if st.session_state.pedido_selecionado_idx == num_ped:
              st.session_state.pedido_selecionado_idx = None

            st.session_state.val_bc1 = ""
            st.session_state.val_bc2 = ""
            st.session_state.val_bc3 = ""

            st.session_state.etapa_validacao = False
            st.session_state.erro_ativo = None
            st.session_state.dados_conferencia = {}
            st.cache_data.clear()
            st.balloons()
            st.success("🎉 Última LPN confirmada! Pedido concluído com sucesso!")
            st.rerun()
          else:
            st.session_state.val_bc1 = ""
            st.session_state.val_bc2 = ""
            st.session_state.val_bc3 = ""

            st.success(
                f"✅ LPN `{lpn_atual}` aceita! Restam"
                f" {total_necessario - len(lpns_lidas_pedido)} LPN(s)."
            )
            st.session_state.etapa_validacao = False
            st.session_state.erro_ativo = None
            st.session_state.dados_conferencia = {}
            st.rerun()
        except Exception as e:
          st.error(f"Erro: {e}")
      else:
        st.error(
            "⚠ Você precisa selecionar 'Sim' em ambas as confirmações para"
            " prosseguir!"
        )

  st.markdown("---")

else:
  # ==========================================
  # TELA 2: PAINEL DE PEDIDOS E VALIDAÇÃO
  # ==========================================
  st.subheader("📋 PAINEL DE PEDIDOS")

  col_tit_painel, col_btn_att = st.columns([5, 1.5])
  with col_tit_painel:
    st.markdown("### Selecione o pedido nas abas abaixo:")

  with col_btn_att:
    gif_base64 = ""
    if os.path.exists(IMAGENS["att_gif"]):
      with open(IMAGENS["att_gif"], "rb") as f:
        gif_base64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-end; align-items: center; margin-top: 5px;">
            <form action="" method="get">
                <button type="submit" name="atualizar_pedidos" value="true" style="
                    background-color: #000000;
                    border: 1.5px solid #00bfff;
                    border-radius: 8px;
                    color: #00bfff;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 6px 12px;
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                ">
                    <img src="data:image/gif;base64,{gif_base64}" width="14px" style="margin-right: 6px; display: inline-block; vertical-align: middle;">
                    ATUALIZAR PEDIDOS
                </button>
            </form>
        </div>
        """,
        unsafe_allow_html=True,
    )

    query_params = st.query_params
    if "atualizar_pedidos" in query_params:
      st.query_params.clear()
      st.cache_data.clear()
      st.rerun()

  mapa_pedidos = {}
  if dados_validos:
    pedidos_pendentes = [
        r for r in dados_validos if not (len(r) > 13 and str(r[13]).strip())
    ]

    fuso_horario_BR = pytz.timezone("America/Sao_Paulo")
    agora_br = datetime.now(fuso_horario_BR)
    pedidos_concluidos_24h = []
    for r in dados_validos:
      if len(r) > 13 and str(r[13]).strip():
        data_conc_str = str(r[13]).strip()
        data_conc_obj = None
        for fmt in (
            "%d/%m/%Y %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y",
            "%Y-%m-%d",
        ):
          try:
            data_conc_obj = datetime.strptime(data_conc_str, fmt)
            break
          except Exception:
            continue
        if data_conc_obj:
          if data_conc_obj.tzinfo is None:
            data_conc_obj = fuso_horario_BR.localize(data_conc_obj)
          if (agora_br - data_conc_obj) <= timedelta(hours=24):
            pedidos_concluidos_24h.append(r)
        else:
          pedidos_concluidos_24h.append(r)

    aba_pendentes, aba_concluidos = st.tabs(
        ["⏳ Pedidos Pendentes", "✅ Pedidos Concluídos"]
    )

    with aba_pendentes:
      if pedidos_pendentes:
        num_colunas = 6
        linhas_cards = [
            pedidos_pendentes[i : i + num_colunas]
            for i in range(0, len(pedidos_pendentes), num_colunas)
        ]
        for bloco in linhas_cards:
          cols = st.columns(num_colunas)
          for i, r in enumerate(bloco):
            idx_p = dados_validos.index(r) + 1
            linha_real = registos.index(r) + 1
            try:
              linha_pedido = r[1] if len(r) > 1 else ""
              cod_material = limpar_texto(r[7] if len(r) > 7 else "")
              dun_material = r[8] if len(r) > 8 else ""

              desc_completa = r[2] if len(r) > 2 else ""
              tres_primeiras = obter_tres_primeiras_palavras(desc_completa)

              data_palete = r[3] if len(r) > 3 else ""

              vencimento_bruto = r[9] if len(r) > 9 else ""
              data_vencimento = formatar_para_aammdd(vencimento_bruto)

              lote = r[10] if len(r) > 10 else ""
              lpn_inteira = r[4] if len(r) > 4 else "0"

              # Exibição condicional da quantidade de quebra
              lista_quebras_card = obter_lista_quebras(r)
              qtd_quebra_html = ""
              if lista_quebras_card:
                valores_quebras_str = ", ".join(map(str, lista_quebras_card))
                qtd_quebra_html = f"<b>QTD QUEBRA:</b> {valores_quebras_str}<br>"

              total_esperado = obter_quantidade_total_lpns(r)
              e_prioridade = len(pedidos_pendentes) > 5
              lpns_ja_lidas = st.session_state.lpns_validadas_por_pedido.get(
                  idx_p, []
              )
              qtd_lidas = len(lpns_ja_lidas)
              porcentagem = min(int((qtd_lidas / total_esperado) * 100), 100)

              hora_solicitacao_bruta = r[0] if len(r) > 0 else ""
              hora_solicitacao = extrair_hora_da_string(hora_solicitacao_bruta)

              mapa_pedidos[idx_p] = {
                  "num_pedido": idx_p,
                  "linha": linha_real,
                  "registro": r,
                  "total_esperado": total_esperado,
              }

              with cols[i]:
                is_selecionado = (
                    st.session_state.pedido_selecionado_idx == idx_p
                )
                classe_card = (
                    "card-pedido"
                    if (is_selecionado or not e_prioridade)
                    else "card-pedido-prioridade"
                )
                destaque_sel = (
                    "border: 2px solid #00bfff; background-color: #16222b;"
                    if is_selecionado
                    else ""
                )
                tag_prioridade_html = (
                    '<span style="color: #ff4b4b; font-weight: bold;">🔴'
                    " URGENTE / PRIORIDADE</span><br>"
                    if e_prioridade
                    else ""
                )

                st.markdown(
                    f"""<div class="{classe_card}" style="{destaque_sel}">
{tag_prioridade_html}
<b>LINHA:</b> {linha_pedido}<br>
<b>MATERIAL:</b> {cod_material}<br>
<b>DESC:</b> {tres_primeiras}<br>
<b>DUN:</b> {dun_material}<br>
<b>DATA:</b> {data_palete}<br>
<b>VENC:</b> {data_vencimento}<br>
<b>LOTE:</b> {lote}<br>
<b>LPN INTEIRA:</b> {lpn_inteira}<br>
{qtd_quebra_html}
<b>Solicitado as:</b> {hora_solicitacao}<br>
<hr style="margin: 6px 0; border-color: #444; border-width: 1px 0 0 0;">
<span style="color: #00bfff;"><b>Progresso: {qtd_lidas}/{total_esperado} ({porcentagem}%)</b></span>
</div>""",
                    unsafe_allow_html=True,
                )

                label_botao_card = (
                    "✔ Selecionado"
                    if is_selecionado
                    else f"Selecionar Pedido {idx_p}"
                )
                if st.button(
                    label_botao_card,
                    key=f"btn_sel_{idx_p}",
                    use_container_width=True,
                ):
                  st.session_state.pedido_selecionado_idx = idx_p
                  st.rerun()
            except Exception:
              continue
      else:
        st.success("Todas os LPNs pendentes já foram validadas e concluídas")

    with aba_concluidos:
      if pedidos_concluidos_24h:
        num_colunas_conc = 6
        linhas_cards_conc = [
            pedidos_concluidos_24h[i : i + num_colunas_conc]
            for i in range(0, len(pedidos_concluidos_24h), num_colunas_conc)
        ]
        for bloco_conc in linhas_cards_conc:
          cols_conc = st.columns(num_colunas_conc)
          for j, rc in enumerate(bloco_conc):
            try:
              linha_pedido_c = rc[1] if len(rc) > 1 else ""
              cod_material_c = limpar_texto(rc[7] if len(rc) > 7 else "")
              desc_completa_c = rc[2] if len(rc) > 2 else ""
              tres_primeiras_c = obter_tres_primeiras_palavras(desc_completa_c)

              lpn_inteira_c = rc[4] if len(rc) > 4 else "0"
              lista_quebras_c = obter_lista_quebras(rc)
              qtd_quebra_conc_html = ""
              if lista_quebras_c:
                valores_quebras_str_c = ", ".join(map(str, lista_quebras_c))
                qtd_quebra_conc_html = (
                    f"<b>QTD QUEBRA:</b> {valores_quebras_str_c}<br>"
                )

              responsavel_c = rc[11] if len(rc) > 11 else ""
              data_conclusao_c = rc[13] if len(rc) > 13 else ""

              with cols_conc[j]:
                st.markdown(
                    f"""<div class="card-pedido-concluido">
<span style="color: #2ecc71; font-weight: bold;">✔ CONCLUÍDO</span><br>
<b>LINHA:</b> {linha_pedido_c}<br>
<b>MATERIAL:</b> {cod_material_c}<br>
<b>DESC:</b> {tres_primeiras_c}<br>
<b>LPN INTEIRA:</b> {lpn_inteira_c}<br>
{qtd_quebra_conc_html}
<b>Responsável:</b> {responsavel_c}<br>
<b>Data:</b> {data_conclusao_c}
</div>""",
                    unsafe_allow_html=True,
                )
            except Exception:
              continue
      else:
        st.info("Nenhum pedido concluído nas últimas 24 horas.")
  else:
    st.info("Nenhuma solicitação encontrada na planilha.")

  st.markdown("---")

  # ==========================================
  # FORMULÁRIO DE LEITURA E VALIDAÇÃO RIGOROSA
  # ==========================================
  col_esq, col_meio, col_dir = st.columns([1.2, 1.2, 1.4], gap="large")

  with col_esq:
    st.subheader("📝 Validar e Dar Baixa na LPN")
    nome_responsavel = st.text_input(
        "Nome",
        value=st.session_state.val_nome,
        placeholder="Digite seu nome...",
        key="input_nome_field",
    )
    st.session_state.val_nome = nome_responsavel

    bc1 = st.text_input(
        "1º Código de Barras (LPN)",
        value=st.session_state.val_bc1,
        key="input_bc1_field",
    )
    st.session_state.val_bc1 = bc1
    bc2 = st.text_input(
        "2º Código de Barras",
        value=st.session_state.val_bc2,
        key="input_bc2_field",
    )
    st.session_state.val_bc2 = bc2
    bc3 = st.text_input(
        "3º Código de Barras",
        value=st.session_state.val_bc3,
        key="input_bc3_field",
    )
    st.session_state.val_bc3 = bc3

    idx_sel_atual = st.session_state.get("pedido_selecionado_idx")
    if idx_sel_atual and idx_sel_atual in mapa_pedidos:
      p_info = mapa_pedidos[idx_sel_atual]
      lidas_atualmente = st.session_state.lpns_validadas_por_pedido.get(
          p_info["num_pedido"], []
      )
      tot_esperado_pedido = p_info["total_esperado"]
      qtd_lidas = len(lidas_atualmente)
      porcentagem_calc = min(int((qtd_lidas / tot_esperado_pedido
