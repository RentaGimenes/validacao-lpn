from datetime import datetime, timedelta
import os
import re
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import pytz
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Definição dos nomes das imagens que uso na tela
IMAGENS = {
    "guia05": "GUIA DE CODIGO DE LPN.JPG",
    "conf_desc": "descricao material.png",
    "conf_ordem": "ordemdeprod.png",
    "material04": "ERRO NO MATERIAL - INCOMPATIVEL COM O SOLICITADO.png",
    "lote06": "LOTE IMCOMPATIVEL COM LA DATA DE VENCIMENTO.png"
    if "LOTE IMCOMPATIVEL COM LA DATA DE VENCIMENTO.png"
    else "lote06.png",
    "datav02": "DATA DE VENCIMENTO NAO ESTA COMPATIVEL.png",
    "datafab03": "DATA DE FABRICAÇÃO NAO ESTA DE ACORDO COM O SOLICITADO.png",
    "dun03": "DUN NAO ESTA CORRESPONDENTE A DUN DO MATERIAL SOLICITADO.png",
    "validacao_qtd": "validação da quantidade.PNG",
}

# Configuro a página do app aqui
st.set_page_config(page_title="Validação de LPN", page_icon="📦", layout="wide")

# Refresh automático a cada 3 minutos
count = st_autorefresh(interval=180000, key="datarefresh")

# Meu CSS customizado
st.markdown(
    """
    <style>
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
    .card-concluido {
        background-color: #1e1e1e;
        border: 2px solid #2ecc71;
        padding: 10px;
        border-radius: 6px;
        font-size: 13px;
        color: #ffffff;
        margin-bottom: 8px;
        text-align: left;
        max-width: 250px;
        margin-left: auto;
        margin-right: auto;
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
    </style>
""",
    unsafe_allow_html=True,
)


def tocar_som_erro():
  sound_html = """
        <audio autoplay>
            <source src="https://assets.mixkit.co/active_storage/sfx/2575/2575-preview.mp3" type="audio/mpeg">
        </audio>
    """
  st.markdown(sound_html, unsafe_allow_html=True)


@st.cache_resource
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


try:
  client = init_connection()
  spreadsheet_name = "SOLICITAÇÃO DE LPN"
  sheet = client.open(spreadsheet_name).worksheet("SOLICITAÇÕES")
except Exception as e:
  st.error(f"Erro ao conectar com o Google Sheets: {e}")
  st.stop()


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


def formatar_data_aammdd(data_str):
  if not data_str:
    return data_str
  data_str = re.sub(r"\D", "", str(data_str))
  if len(data_str) != 6:
    return data_str
  try:
    ano = "20" + data_str[0:2]
    mes = data_str[2:4]
    dia = data_str[4:6]
    datetime(int(ano), int(mes), int(dia))
    return f"{dia}/{mes}/{ano}"
  except Exception:
    return data_str


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
      ano = int("20" + partes[0])
      mes = int(partes[1])
      dia = int(partes[2])
      return datetime(ano, mes, dia).date()
    except Exception:
      pass

  if len(data_str) == 6 and data_str.isdigit():
    try:
      ano = int("20" + data_str[0:2])
      mes = int(data_str[2:4])
      dia = int(data_str[4:6])
      return datetime(ano, mes, dia).date()
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


def processar_codigo_1(barcode):
  return barcode.replace("(", "").replace(")", "").strip()


def processar_codigo_2(barcode):
  try:
    limpo = barcode.replace("(", "").replace(")", "")

    match_mat = re.search(r"90(\d+?)(?=37|$)", limpo)
    mat = match_mat.group(1) if match_mat else limpo[2:10]

    match_qtd = re.search(r"37(\d+)", limpo)
    if match_qtd:
      bloco_qtd = match_qtd.group(1)
      quantidade = int(bloco_qtd.lstrip("0") or "0")
    else:
      quantidade = 0

    match_lote = re.search(r"10(\d+)", limpo)
    if match_lote:
      bloco_lote = match_lote.group(1)
      lote = bloco_lote.lstrip("0") or bloco_lote
    else:
      lote = ""

    return limpar_texto(mat), quantidade, limpar_texto(lote)[:7]
  except Exception:
    return "", 0, ""


def processar_codigo_3(barcode):
  try:
    limpo = barcode.replace("(", "").replace(")", "")

    match_dun = re.search(r"(?:^|\D)02(\d{14})", limpo)
    if match_dun:
      dun = match_dun.group(1)
    else:
      match_dun_alt = re.search(r"02(\d+?)(?=17|11|$)", limpo)
      dun = match_dun_alt.group(1) if match_dun_alt else limpo[2:16]

    match_venc = re.search(r"17(\d{6})", limpo)
    vencimento = match_venc.group(1) if match_venc else ""

    matches_fab = re.findall(r"11(\d{6})", limpo)
    fabricacao = matches_fab[-1] if matches_fab else ""

    return limpar_texto(dun), limpar_texto(vencimento), limpar_texto(fabricacao)
  except Exception:
    return "", "", ""


def obter_lista_quebras(r):
  try:
    texto_quebras = str(r[6]).strip() if len(r) > 6 else ""
    if not texto_quebras or texto_quebras == "0":
      return []
    partes = [
        int(re.sub(r"\D", "", p))
        for p in texto_quebras.split(",")
        if p.strip() and re.sub(r"\D", "", p).isdigit()
    ]
    return partes
  except Exception:
    return []


def obter_quantidade_inteira(r):
  try:
    val_inteiros = (
        int(re.sub(r"\D", "", str(r[4])))
        if len(r) > 4 and str(r[4]).strip()
        else 0
    )
  except Exception:
    val_inteiros = 0
  return val_inteiros


def obter_quantidade_total_lpns(r):
  val_inteiros = obter_quantidade_inteira(r)
  lista_quebras = obter_lista_quebras(r)
  total = val_inteiros + len(lista_quebras)
  return total if total > 0 else 1


st.markdown("## 📦 Validação das informações das Lpn")

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

registos = []
dados_validos = []
try:
  registos = sheet.get_all_values()
  if len(registos) > 1:
    for r in registos[1:]:
      if any(str(celula).strip() for celula in r):
        dados_validos.append(r)
except Exception as e:
  st.warning(f"Aviso ao carregar dados da planilha: {e}")

aba_painel, aba_concluidos = st.tabs(
    ["📋 Painel Principal e Validação", "🕒 Concluídos nas Últimas 24h"]
)

with aba_painel:
  st.subheader("📋 Painel de Solicitações Pendentes")

  mapa_pedidos = {}
  if dados_validos:
    pedidos_pendentes = [
        r for r in dados_validos if not (len(r) > 13 and r[13].strip())
    ]
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
            cod_material = r[7] if len(r) > 7 else ""

            desc_completa = r[2] if len(r) > 2 else ""
            desc_resumida = (
                (desc_completa[:22] + "...")
                if len(desc_completa) > 22
                else desc_completa
            )

            data_palete = r[3] if len(r) > 3 else ""
            data_vencimento = r[9] if len(r) > 9 else ""
            lote = r[10] if len(r) > 10 else ""
            lpn_inteira = r[4] if len(r) > 4 else "0"
            quebra_txt = r[6] if len(r) > 6 else "0"

            total_esperado = obter_quantidade_total_lpns(r)
            e_prioridade = len(pedidos_pendentes) > 5

            lpns_ja_lidas = st.session_state.lpns_validadas_por_pedido.get(
                idx_p, []
            )
            qtd_lidas = len(lpns_ja_lidas)
            porcentagem = min(int((qtd_lidas / total_esperado) * 100), 100)

            mapa_pedidos[idx_p] = {
                "num_pedido": idx_p,
                "linha": linha_real,
                "registro": r,
                "total_esperado": total_esperado,
            }

            with cols[i]:
              is_selecionado = st.session_state.pedido_selecionado_idx == idx_p

              if is_selecionado:
                destaque_sel = (
                    "border: 2px solid #2ecc71; box-shadow: 0 0 10px #2ecc71;"
                )
                classe_card = "card-pedido"
              elif e_prioridade:
                classe_card = "card-pedido-prioridade"
                destaque_sel = ""
              else:
                classe_card = "card-pedido"
                destaque_sel = ""

              tag_prioridade_html = (
                  '<span style="color: #ff4b4b; font-weight: bold;">🔴'
                  " URGENTE / PRIORIDADE</span><br>"
                  if e_prioridade
                  else ""
              )

              with st.container():
                st.markdown(
                    f"""<div class="{classe_card}" style="{destaque_sel}">
{tag_prioridade_html}
<b>Linha:</b> {linha_pedido}<br>
<b>Cód Mat:</b> {cod_material}<br>
<b>Desc:</b> {desc_resumida}<br>
<b>Data Palete:</b> {data_palete}<br>
<b>Venc:</b> {data_vencimento}<br>
<b>Lote:</b> {lote}<br>
<b>LPN Inteira:</b> {lpn_inteira}<br>
<b>Quebra:</b> {quebra_txt}<br>
<hr style="margin: 6px 0; border-color: #444; border-width: 1px 0 0 0;">
<span style="color: #f1c40f;"><b>Progresso: {qtd_lidas}/{total_esperado} ({porcentagem}%)</b></span>
</div>""",
                    unsafe_allow_html=True,
                )

              label_botao = (
                  "✅ Selecionado"
                  if is_selecionado
                  else f"Selecionar Pedido {idx_p}"
              )
              if st.button(
                  label_botao, key=f"btn_sel_{idx_p}", use_container_width=True
              ):
                st.session_state.pedido_selecionado_idx = idx_p
                st.rerun()

          except Exception:
            continue
    else:
      st.success("🎉 Todos os pedidos já foram validados e concluídos!")
  else:
    st.info("Nenhuma solicitação encontrada na planilha.")

  st.markdown("---")

  if st.session_state.etapa_validacao:
    st.subheader("🔍 Confirmação Visual Obrigatória")
    d = st.session_state.dados_conferencia

    st.success(f"✔ Validando LPN para o **Pedido {d['num_pedido']}**!")

    st.markdown(
        f'📦 **LPN Atual:** <span class="texto-destaque-lpn">{d["lpn"]}</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'🏷 **Material:** <span class="texto-destaque-mat">{d["descricao"]}</span>',
        unsafe_allow_html=True,
    )

    col_conf1, col_conf2 = st.columns(2)

    with col_conf1:
      resp_desc_str = st.radio(
          "📌 A descrição está correta?",
          ["Selecione...", "Sim", "Não"],
          horizontal=True,
          key="r_desc",
      )
      img_desc = IMAGENS["conf_desc"]
      if os.path.exists(img_desc):
        st.image(img_desc, width=420)
      else:
        st.warning(f"⚠ Imagem `{img_desc}` não encontrada.")

    with col_conf2:
      resp_ordem_str = st.radio(
          "📌 Você verificou a ordem?",
          ["Selecione...", "Sim", "Não"],
          horizontal=True,
          key="r_ordem",
      )
      img_ordem = IMAGENS["conf_ordem"]
      if os.path.exists(img_ordem):
        st.image(img_ordem, width=420)
      else:
        st.warning(f"⚠ Imagem `{img_ordem}` não encontrada.")

    if st.button("Confirmar esta LPN", type="primary", use_container_width=True):
      if resp_ordem_str == "Sim" and resp_desc_str == "Sim":
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

          lpns_lidas_pedido = st.session_state.lpns_validadas_por_pedido[num_ped]

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

            st.session_state.etapa_validacao = False
            st.session_state.erro_ativo = None
            if "dados_conferencia" in st.session_state:
              del st.session_state.dados_conferencia

            for k in ["input_bc1", "input_bc2", "input_bc3"]:
              st.session_state[k] = ""

            st.cache_data.clear()
            st.balloons()
            st.success("🎉 Última LPN confirmada! Pedido concluído com sucesso!")
            st.rerun()
          else:
            st.success(
                f"✅ LPN `{lpn_atual}` aceita! Restam"
                f" {total_necessario - len(lpns_lidas_pedido)} LPN(s) para este"
                " pedido."
            )
            st.session_state.etapa_validacao = False
            st.session_state.erro_ativo = None
            if "dados_conferencia" in st.session_state:
              del st.session_state.dados_conferencia

            for k in ["input_bc1", "input_bc2", "input_bc3"]:
              st.session_state[k] = ""

            st.rerun()

        except Exception as e:
          st.error(f"Erro: {e}")
      else:
        st.error("⚠ Selecione 'Sim' em ambas as confirmações!")
    st.markdown("---")

  col_form, col_img = st.columns(2)
  with col_form:
    st.subheader("📝 Validar e Dar Baixa na LPN")
    nome_responsavel = st.text_input("Nome", placeholder="Digite seu nome...")

    idx_sel_atual = st.session_state.get("pedido_selecionado_idx")
    if idx_sel_atual and idx_sel_atual in mapa_pedidos:
      p_sel = mapa_pedidos[idx_sel_atual]
      mat_s = p_sel["registro"][2] if len(p_sel["registro"]) > 2 else "N/D"
      linha_s = p_sel["registro"][1] if len(p_sel["registro"]) > 1 else "N/D"
      st.markdown(
          f"🎯 **Pedido Selecionado:** Pedido {idx_sel_atual} (Linha:"
          f" {linha_s} - Mat: {mat_s})"
      )

    def executar_validacao():
      bc1_val = st.session_state.get("input_bc1", "").strip()
      bc2_val = st.session_state.get("input_bc2", "").strip()
      bc3_val = st.session_state.get("input_bc3", "").strip()

      if not nome_responsavel.strip():
        st.warning("⚠️ Digite o seu nome.")
        return

      idx_sel = st.session_state.get("pedido_selecionado_idx")
      if not idx_sel or idx_sel not in mapa_pedidos:
        st.warning(
            "⚠ Selecione um pedido clicando no cartão correspondente no painel"
            " acima."
        )
        return

      if not bc1_val or not bc2_val or not bc3_val:
        st.warning("⚠ Preencha os 3 códigos de barras.")
        return

      lpn_lida = processar_codigo_1(bc1_val)
      mat_lido, qtd_lida, lote_lido = processar_codigo_2(bc2_val)
      dun_lido, venc_lido, fab_lido = processar_codigo_3(bc3_val)

      info_pedido = mapa_pedidos[idx_sel]
      linha_encontrada = info_pedido["linha"]
      num_pedido_escolhido = info_pedido["num_pedido"]
      r_escolhido = info_pedido["registro"]
      total_necessario = info_pedido["total_esperado"]

      lpns_ja_lidas = st.session_state.lpns_validadas_por_pedido.get(
          num_pedido_escolhido, []
      )

      # -------------------------------------------------------------
      # LÓGICA INTELIGENTE: INTEIRAS vs QUEBRAS (ORDEM ALEATÓRIA)
      # -------------------------------------------------------------
      qtd_inteira_esperada = obter_quantidade_inteira(r_escolhido)
      lista_quebras = obter_lista_quebras(r_escolhido)

      if len(lpns_ja_lidas) < qtd_inteira_esperada:
        pass
      else:
        if len(lista_quebras) > 0:
          if qtd_lida not in lista_quebras:
            st.session_state.erro_ativo = "validacao_qtd"
            st.session_state.detalhes_erro = {
                "solicitado": f"Quebras esperadas pendentes: {lista_quebras}",
                "lido": f"Quantidade informada no BC2 (37): {qtd_lida}",
            }
            tocar_som_erro()
            return
        else:
          st.session_state.erro_ativo = "limite"
          st.session_state.detalhes_erro = {
              "solicitado": f"Limite Máximo Atingido: {total_necessario} LPNs",
              "lido": f"Tentativa excedida com a LPN: {lpn_lida}",
          }
          tocar_som_erro()
          return

      if lpn_lida in lpns_ja_lidas:
        st.session_state.erro_ativo = "lpn_duplicada"
        st.session_state.detalhes_erro = {
            "solicitado": "",
            "lido": f"LPN já validada anteriormente: {lpn_lida}",
        }
        tocar_som_erro()
        return

      mat_planilha = limpar_texto(r_escolhido[7] if len(r_escolhido) > 7 else "")
      lote_planilha = limpar_texto(
          r_escolhido[10] if len(r_escolhido) > 10 else ""
      )
      data_vencimento_planilha_raw = r_escolhido[9] if len(r_escolhido) > 9 else ""
      data_fabricacao_planilha_raw = r_escolhido[3] if len(r_escolhido) > 3 else ""
      dun_planilha = limpar_texto(r_escolhido[8] if len(r_escolhido) > 8 else "")

      if not mat_lido or mat_lido != mat_planilha:
        st.session_state.erro_ativo = "material04"
        st.session_state.detalhes_erro = {
            "solicitado": mat_planilha or "(Vazio na planilha)",
            "lido": mat_lido or "(Não identificado)",
        }
        tocar_som_erro()
        return

      if dun_planilha and dun_lido and dun_lido != dun_planilha:
        st.session_state.erro_ativo = "dun03"
        st.session_state.detalhes_erro = {
            "solicitado": dun_planilha,
            "lido": dun_lido,
        }
        tocar_som_erro()
        return

      if lote_planilha and lote_lido and lote_lido != lote_planilha:
        st.session_state.erro_ativo = "lote06"
        st.session_state.detalhes_erro = {
            "solicitado": lote_planilha,
            "lido": lote_lido,
        }
        tocar_som_erro()
        return

      if data_vencimento_planilha_raw and venc_lido:
        data_obj_planilha = converter_para_data_obj(data_vencimento_planilha_raw)
        data_obj_lida = converter_para_data_obj(venc_lido)

        if data_obj_planilha and data_obj_lida:
          if data_obj_lida != data_obj_planilha:
            st.session_state.erro_ativo = "datav02"
            st.session_state.detalhes_erro = {
                "solicitado": str(data_vencimento_planilha_raw),
                "lido": formatar_data_aammdd(venc_lido),
            }
            tocar_som_erro()
            return

      if data_fabricacao_planilha_raw and fab_lido:
        data_fab_obj_planilha = converter_para_data_obj(
            data_fabricacao_planilha_raw
        )
        data_fab_obj_lida = converter_para_data_obj(fab_lido)

        if data_fab_obj_planilha and data_fab_obj_lida:
          if data_fab_obj_lida != data_fab_obj_planilha:
            st.session_state.erro_ativo = "datafab03"
            st.session_state.detalhes_erro = {
                "solicitado": str(data_fabricacao_planilha_raw),
                "lido": formatar_data_aammdd(fab_lido),
            }
            tocar_som_erro()
            return
        else:
          st.session_state.erro_ativo = "datafab03"
          st.session_state.detalhes_erro = {
              "solicitado": str(data_fabricacao_planilha_raw),
              "lido": str(fab_lido),
          }
          tocar_som_erro()
          return

      st.session_state.erro_ativo = None
      st.session_state.detalhes_erro = {"solicitado": "", "lido": ""}
      st.session_state.dados_conferencia = {
          "linha": linha_encontrada,
          "num_pedido": num_pedido_escolhido,
          "responsavel": nome_responsavel.strip(),
          "lpn": lpn_lida,
          "quantidade_extraida": qtd_lida,
          "descricao": r_escolhido[2] if len(r_escolhido) > 2 else "",
          "total_esperado": total_necessario,
      }
      st.session_state.etapa_validacao = True
      st.rerun()

    # Garante a existência das chaves de input no session_state
    for k in ["input_bc1", "input_bc2", "input_bc3"]:
      if k not in st.session_state:
        st.session_state[k] = ""

    bc1 = st.text_input(
        "1º Código de Barras (LPN)",
        key="input_bc1",
    )
    bc2 = st.text_input(
        "2º Código de Barras",
        key="input_bc2",
    )
    bc3 = st.text_input(
        "3º Código de Barras",
        key="input_bc3",
    )

    texto_botao_validar = "Validar LPN"
    if idx_sel_atual and idx_sel_atual in mapa_pedidos:
      p_info = mapa_pedidos[idx_sel_atual]
      lidas_atualmente = st.session_state.lpns_validadas_por_pedido.get(
          p_info["num_pedido"], []
      )
      tot_esperado_pedido = p_info["total_esperado"]
      qtd_lidas = len(lidas_atualmente)

      if qtd_lidas > 0:
        texto_botao_validar = "Validar Próxima LPN"

      porcentagem_calc = min(int((qtd_lidas / tot_esperado_pedido) * 100), 100)
      st.markdown(
          f"**Progresso:** {qtd_lidas} de {tot_esperado_pedido} LPNs"
          f" ({porcentagem_calc}%)"
      )
      st.progress(porcentagem_calc / 100.0)

    if st.button(texto_botao_validar, type="primary", use_container_width=True):
      executar_validacao()
      # Se passou da validação inicial sem erro grave, limpa os campos via session_state e força refresh
      if not st.session_state.get("erro_ativo") and not st.session_state.get(
          "etapa_validacao"
      ):
        st.session_state["input_bc1"] = ""
        st.session_state["input_bc2"] = ""
        st.session_state["input_bc3"] = ""
        st.rerun()

  with col_img:
    erro = st.session_state.get("erro_ativo")
    det = st.session_state.get("detalhes_erro", {"solicitado": "", "lido": ""})

    if erro == "material04":
      st.markdown(
          '<div class="alerta-piscar">🚫 Erro no Material</div>',
          unsafe_allow_html=True,
      )
      st.markdown(
          '<div class="alerta-sub">Incompatível com o solicitado.</div>',
          unsafe_allow_html=True,
      )
      st.markdown(
          f"""
                <div class="alerta-comparacao">
                    <b>SOLICITADO:</b> {det['solicitado']}<br>
                    <b>Gerado na LPN:</b> {det['lido']}
                </div>
            """,
          unsafe_allow_html=True,
      )
      img_nome = IMAGENS["material04"]
      if os.path.exists(img_nome):
        st.image(img_nome, width=450)
      else:
        st.warning(f"⚠ Imagem `{img_nome}` não encontrada.")

    elif erro == "lote06":
      st.markdown(
          '<div class="alerta-piscar">🚫 Erro de Lote</div>',
          unsafe_allow_html=True,
      )
      st.markdown(
          '<div class="alerta-sub">Imcompatível com a data de vencimento.</div>',
          unsafe_allow_html=True,
      )
      st.markdown(
          f"""
                <div class="alerta-comparacao">
                    <b>SOLICITADO:</b> {det['solicitado']}<br>
                    <b>Gerado na LPN:</b> {det['lido']}
                </div>
            """,
          unsafe_allow_html=True,
      )
      img_nome = IMAGENS["lote06"]
      if os.path.exists(img_nome):
        st.image(img_nome, width=450)
      else:
        st.warning(f"⚠ Imagem `{img_nome}` não encontrada.")

    elif erro == "datav02":
      st.markdown(
          '<div class="alerta-piscar">🚫 Erro de Data de Validade</div>',
          unsafe_allow_html=True,
      )
      st.markdown(
          '<div class="alerta-sub">Data de vencimento não está compatível.</div>',
          unsafe_allow_html=True,
      )
      st.markdown(
          f"""
                <div class="alerta-comparacao">
                    <b>SOLICITADO:</b> {det['solicitado']}<br>
                    <b>Gerado na LPN:</b> {det['lido']}
                </div>
            """,
          unsafe_allow_html=True,
      )
      img_nome = IMAGENS["datav02"]
      if os.path.exists(img_nome):
        st.image(img_nome, width=450)
      else:
        st.warning(f"⚠ Imagem `{img_nome}` não encontrada.")

    elif erro == "datafab03":
      st.markdown(
          '<div class="alerta-piscar">🚫 Erro de Data de Fabricação</div>',
          unsafe_allow_html=True,
      )
      st.markdown(
          '<div class="alerta-sub">Data de fabricação não está de acordo com o solicitado.</div>',
          unsafe_allow_html=True,
      )
      st.markdown(
          f"""
                <div class="alerta-comparacao">
                    <b>SOLICITADO:</b> {det['solicitado']}<br>
                    <b>Gerado na LPN:</b> {det['lido']}
                </div>
            """,
          unsafe_allow_html=True,
      )
      img_nome = IMAGENS["datafab03"]
      if os.path.exists(img_nome):
        st.image(img_nome, width=450)
      else:
        st.warning(f"⚠ Imagem `{img_nome}` não encontrada.")

    elif erro == "dun03":
      st.markdown(
          '<div class="alerta-piscar">🚫 Erro de DUN</div>',
          unsafe_allow_html=True,
      )
      st.markdown(
          '<div class="alerta-sub">DUN não está correspondente à DUN do material solicitado.</div>',
          unsafe_allow_html=True,
      )
      st.markdown(
          f"""
                <div class="alerta-comparacao">
                    <b>SOLICITADO:</b> {det['solicitado']}<br>
                    <b>Gerado na LPN:</b> {det['lido']}
                </div>
            """,
          unsafe_allow_html=True,
      )
      img_nome = IMAGENS["dun03"]
      if os.path.exists(img_nome):
        st.image(img_nome, width=450)
      else:
        st.warning(f"⚠️ Imagem `{img_nome}` não encontrada.")

    elif erro == "lpn_duplicada":
      st.markdown(
          '<div class="alerta-piscar">🚫 LPN Duplicada</div>',
          unsafe_allow_html=True,
      )
      st.markdown(
          f"""
                <div class="alerta-comparacao">
                    <b>{det['lido']}</b>
                </div>
            """,
          unsafe_allow_html=True,
      )
      img_qtd = IMAGENS["validacao_qtd"]
      if os.path.exists(img_qtd):
        st.image(img_qtd, width=450)
      else:
        img_fallback = IMAGENS["material04"]
        if os.path.exists(img_fallback):
          st.image(img_fallback, width=450)

    elif erro == "limite" or erro == "validacao_qtd":
      st.markdown(
          '<div class="alerta-piscar">🚫 Validação de Quantidade / LPN</div>',
          unsafe_allow_html=True,
      )
      st.markdown(
          '<div class="alerta-sub">LPN\'s inteiras desse pedido já foram validadas.</div>',
          unsafe_allow_html=True,
      )
      st.markdown(
          f"""
                <div class="alerta-comparacao">
                    <b>SOLICITADO:</b> {det['solicitado']}<br>
                    <b>Gerado na LPN:</b> {det['lido']}
                </div>
            """,
          unsafe_allow_html=True,
      )
      img_qtd = IMAGENS["validacao_qtd"]
      if os.path.exists(img_qtd):
        st.image(img_qtd, width=450)
      else:
        img_fallback = IMAGENS["material04"]
        if os.path.exists(img_fallback):
          st.image(img_fallback, width=450)

    else:
      st.subheader("💡 Exemplo de LPN")
      img_guia = IMAGENS["guia05"]
      if os.path.exists(img_guia):
        st.image(img_guia, width=450)
      else:
        st.warning(
            f"⚠ Salve a imagem com o nome `{img_guia}` na mesma pasta do script."
        )

with aba_concluidos:
  st.subheader("🕒 Histórico de Pedidos Concluídos (Últimas 24 Horas)")
  if dados_validos:
    fuso_horario = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(fuso_horario)
    concluidos_recentes = []
    for r in dados_validos:
      try:
        data_str = r[13].strip() if len(r) > 13 else ""
        if data_str:
          data_limpa = re.sub(r"\s*\(.*?\)", "", data_str).strip()
          data_conclusao = datetime.strptime(data_limpa, "%d/%m/%Y %H:%M:%S")
          data_conclusao = fuso_horario.localize(data_conclusao)
          if (agora - data_conclusao) <= timedelta(hours=24):
            concluidos_recentes.append((r, data_limpa))
      except Exception:
        continue

    if concluidos_recentes:
      num_colunas = 6
      linhas_cards_conc = [
          concluidos_recentes[i : i + num_colunas]
          for i in range(0, len(concluidos_recentes), num_colunas)
      ]
      for bloco in linhas_cards_conc:
        cols = st.columns(num_colunas)
        for i, (r, data_str) in enumerate(bloco):
          linha_pedido = r[1] if len(r) > 1 else ""
          cod_material = r[7] if len(r) > 7 else ""

          desc_completa_c = r[2] if len(r) > 2 else ""
          desc_resumida_c = (
              (desc_completa_c[:22] + "...")
              if len(desc_completa_c) > 22
              else desc_completa_c
          )

          data_palete = r[3] if len(r) > 3 else ""
          data_vencimento = r[9] if len(r) > 9 else ""
          lote = r[10] if len(r) > 10 else ""
          lpn_inteira = r[4] if len(r) > 4 else "0"
          quebra_txt = r[6] if len(r) > 6 else "0"
          responsavel = r[11] if len(r) > 11 else "N/D"

          with cols[i]:
            st.markdown(
                f"""
                            <div class="card-concluido">
                                <b>Linha:</b> {linha_pedido}<br>
                                <b>Cód Mat:</b> {cod_material}<br>
                                <b>Desc:</b> {desc_resumida_c}<br>
                                <b>Data Palete:</b> {data_palete}<br>
                                <b>Venc:</b> {data_vencimento}<br>
                                <b>Lote:</b> {lote}<br>
                                <b>LPN Inteira:</b> {lpn_inteira}<br>
                                <b>Quebras:</b> {quebra_txt}<br>
                                <hr style="margin: 6px 0; border-color: #444; border-width: 1px 0 0 0;">
                                <b>Resp:</b> {responsavel}<br>
                                <span style="font-size: 11px; color: #aaaaaa;">🕒 {data_str}</span>
                            </div>
                            """,
                unsafe_allow_html=True,
            )
    else:
      st.info("Nenhum pedido concluído nas últimas 24 horas.")
  else:
    st.info("Nenhum dado encontrado.")

st.markdown("---")
st.markdown(
    """
    <div style="display: flex; justify-content: center; align-items: center; gap: 8px; margin-top: 15px; margin-bottom: 10px;">
        <span style="font-size: 11px; color: #777777;">Validação de LPN a todo vapor</span>
        <img src="https://i.pinimg.com/originals/84/90/f0/8490f0cab98f44a6e905a72cb61b72aa.gif" width="40" style="border-radius: 2px;">
    </div>
    """,
    unsafe_allow_html=True,
)
