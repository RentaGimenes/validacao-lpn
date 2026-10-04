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

# Configura a pagina do streamlit pra usar o layout largo
st.set_page_config(page_title="Validação de LPN", page_icon="📦", layout="wide")

# ==========================================
# MAPEAMENTO DE IMAGENS E ARQUIVOS
# ==========================================
# Aqui a gente mapeia os nomes das imagens para facilitar na hora de exibir
IMAGENS = {
    "guia05": "GUIA DE CODIGO DE LPN.JPG",
    "conf_desc": "descricao material.png",
    "conf_ordem": "ordemdeprod.png",
    "material04": "ERRO NO MATERIAL - INCOMPATIVEL COM O SOLICITADO.png",
    "lote06": "LOTE IMCOMPATIVEL COM LA DATA DE VENCIMENTO.png" if os.path.exists("LOTE IMCOMPATIVEL COM LA DATA DE VENCIMENTO.png") else "lote06.png",
    "datav02": "DATA DE VENCIMENTO NAO ESTA COMPATIVEL.png",
    "datafab03": "DATA DE FABRICAÇÃO NAO ESTA DE ACORDO COM O SOLICITADO.png",
    "dun03": "DUN NAO ESTA CORRESPONDENTE A DUN DO MATERIAL SOLICITADO.png",
    "validacao_qtd": "validação da quantidade.PNG",
    "lpn_duplicada": "lpnduplicada.PNG",
    "sonic_gif": "sonicgif/SONICGIF.gif",
    "att_gif": "att.gif",
    "validar_btn": "validar.png",
}

# Atualiza a página automaticamente a cada 3 minutos para pegar dados novos
count = st_autorefresh(interval=180000, key="datarefresh")

# ==========================================
# ESTILOS VISUAIS (CSS CUSTOMIZADO)
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

    /* Centralização das colunas */
    .container-coluna-meio {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        text-align: center;
    }
    .container-coluna-meio img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .container-coluna-direita {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        text-align: center;
    }
    .container-botao-imagem {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }
    .btn-neon-img {
        display: block;
        border-radius: 16px;
        mix-blend-mode: screen; 
        background: rgba(0, 255, 100, 0.15);
        border: 2px solid #00ff66;
        box-shadow: 0 0 12px rgba(0, 255, 100, 0.6), inset 0 0 8px rgba(0, 255, 100, 0.4);
        transition: all 0.2s ease-in-out;
        margin: 0 auto;
    }
    .btn-neon-img:hover {
        box-shadow: 0 0 20px rgba(0, 255, 100, 0.9), inset 0 0 12px rgba(0, 255, 100, 0.6);
        background: rgba(0, 255, 100, 0.25);
    }
    </style>
""", unsafe_allow_html=True)

# Função simples para tocar som de erro na tela quando algo der errado
def tocar_som_erro():
    sound_html = """
        <audio autoplay>
            <source src="https://assets.mixkit.co/active_storage/sfx/2575/2575-preview.mp3" type="audio/mpeg">
        </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# Conexão com o Google Sheets usando os secrets do Streamlit
@st.cache_resource
def init_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
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

# ==========================================
# FUNÇÕES AUXILIARES DE TRATAMENTO
# ==========================================
def limpar_texto(texto):
    if not texto: return ""
    return str(texto).replace(".", "").replace("/", "").replace("-", "").replace(" ", "").strip()

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

def processar_codigo_1(barcode):
    return barcode.replace("(", "").replace(")", "").strip()

def processar_codigo_2(barcode):
    try:
        limpo = barcode.replace("(", "").replace(")", "")
        match_mat = re.search(r'90(\d+?)(?=37|$)', limpo)
        mat = match_mat.group(1) if match_mat else limpo[2:10]
        match_qtd = re.search(r'37(\d+)', limpo)
        quantidade = int(match_qtd.group(1).lstrip('0') or '0') if match_qtd else 0
        match_lote = re.search(r'10(\d+)', limpo)
        lote = match_lote.group(1).lstrip('0') or match_lote.group(1) if match_lote else ""
        return limpar_texto(mat), quantidade, limpar_texto(lote)[:7]
    except Exception:
        return "", 0, ""

def processar_codigo_3(barcode):
    try:
        limpo = barcode.replace("(", "").replace(")", "")
        match_dun = re.search(r'(?:^|\D)02(\d{14})', limpo)
        dun = match_dun.group(1) if match_dun else (re.search(r'02(\d+?)(?=17|11|$)', limpo).group(1) if re.search(r'02(\d+?)(?=17|11|$)', limpo) else limpo[2:16])
        match_venc = re.search(r'17(\d{6})', limpo)
        vencimento = match_venc.group(1) if match_venc else ""
        matches_fab = re.findall(r'11(\d{6})', limpo)
        fabricacao = matches_fab[-1] if matches_fab else ""
        return limpar_texto(dun), limpar_texto(vencimento), limpar_texto(fabricacao)
    except Exception:
        return "", "", ""

def obter_lista_quebras(r):
    try:
        texto_quebras = str(r[6]).strip() if len(r) > 6 else ""
        if not texto_quebras or texto_quebras == "0": return []
        return [int(re.sub(r'\D', '', p)) for p in texto_quebras.split(',') if p.strip() and re.sub(r'\D', '', p).isdigit()]
    except Exception:
        return []

def obter_quantidade_inteira(r):
    try:
        return int(re.sub(r'\D', '', str(r[4]))) if len(r) > 4 and str(r[4]).strip() else 0
    except Exception:
        return 0

def obter_quantidade_total_lpns(r):
    total = obter_quantidade_inteira(r) + len(obter_lista_quebras(r))
    return total if total > 0 else 1

# ==========================================
# TÍTULO PRINCIPAL
# ==========================================
st.markdown("<h2 style='margin-top: 0px; padding-top: 0px;'>📦 Validação das informações das Lpn</h2>", unsafe_allow_html=True)

# Inicializa os estados da sessão
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

# Puxa os dados da planilha do Google
registos, dados_validos = [], []
try:
    registos = sheet.get_all_values()
    if len(registos) > 1:
        for r in registos[1:]:
            if any(str(celula).strip() for celula in r):
                dados_validos.append(r)
except Exception as e:
    st.warning(f"Aviso ao carregar dados da planilha: {e}")

# ==========================================
# FLUXO 1: ETAPA DE CONFIRMAÇÃO VISUAL
# ==========================================
if st.session_state.etapa_validacao:
    st.subheader("🔍 Confirmação Visual Obrigatória")
    d = st.session_state.dados_conferencia
    st.success(f"✔ Validando LPN para o **Pedido {d['num_pedido']}**!")
    
    sonic_path = IMAGENS["sonic_gif"] if os.path.exists(IMAGENS["sonic_gif"]) else "SONICGIF.gif"
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
    
    st.markdown(f'📦 **LPN Atual:** <span class="texto-destaque-lpn">{d["lpn"]}</span>', unsafe_allow_html=True)
    st.markdown(f'🏷 **Material:** <span class="texto-destaque-mat">{d["descricao"]}</span>', unsafe_allow_html=True)

    col_conf1, col_conf2, col_btn_quadrado = st.columns([2, 2, 1])
    
    with col_conf1:
        st.markdown('<div class="box-pergunta-container">', unsafe_allow_html=True)
        st.markdown("📌 **A descrição está correta?**")
        resp_desc = st.radio("A descrição está correta?", ["Sim", "Não"], key="resp_desc_val", horizontal=True, label_visibility="collapsed")
        if os.path.exists(IMAGENS["conf_desc"]): st.image(IMAGENS["conf_desc"], width=420)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_conf2:
        st.markdown('<div class="box-pergunta-container">', unsafe_allow_html=True)
        st.markdown("📌 **Você verificou a ordem?**")
        resp_ordem = st.radio("Você verificou a ordem?", ["Sim", "Não"], key="resp_ordem_val", horizontal=True, label_visibility="collapsed")
        if os.path.exists(IMAGENS["conf_ordem"]): st.image(IMAGENS["conf_ordem"], width=420)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_btn_quadrado:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Confirmar esta LPN", key="btn_confirmar_etapa_visual"):
            if resp_ordem == "Sim" and resp_desc == "Sim":
                try:
                    linha, num_ped, lpn_atual, responsavel_acao, total_necessario = d["linha"], d["num_pedido"], d["lpn"], d["responsavel"], d["total_esperado"]
                    if num_ped not in st.session_state.lpns_validadas_por_pedido: st.session_state.lpns_validadas_por_pedido[num_ped] = []
                    if lpn_atual not in st.session_state.lpns_validadas_por_pedido[num_ped]: st.session_state.lpns_validadas_por_pedido[num_ped].append(lpn_atual)
                    
                    lpns_lidas_pedido = st.session_state.lpns_validadas_por_pedido[num_ped]
                    if len(lpns_lidas_pedido) >= total_necessario:
                        fuso_horario = pytz.timezone("America/Sao_Paulo")
                        hora_atual = datetime.now(fuso_horario).strftime("%d/%m/%Y %H:%M:%S")
                        todas_lpns_str = ", ".join(lpns_lidas_pedido)
                        
                        sheet.update_cell(linha, 12, responsavel_acao)
                        sheet.update_cell(linha, 13, todas_lpns_str)
                        sheet.update_cell(linha, 14, hora_atual)
                        
                        if num_ped in st.session_state.lpns_validadas_por_pedido: del st.session_state.lpns_validadas_por_pedido[num_ped]
                        if st.session_state.pedido_selecionado_idx == num_ped: st.session_state.pedido_selecionado_idx = None
                        
                        st.session_state.etapa_validacao = False
                        st.session_state.erro_ativo = None
                        st.session_state.dados_conferencia = {}
                        st.cache_data.clear()
                        st.balloons()
                        st.success("🎉 Última LPN confirmada! Pedido concluído com sucesso!")
                        st.rerun()
                    else:
                        st.success(f"✅ LPN `{lpn_atual}` aceita! Restam {total_necessario - len(lpns_lidas_pedido)} LPN(s).")
                        st.session_state.etapa_validacao = False
                        st.session_state.erro_ativo = None
                        st.session_state.dados_conferencia = {}
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
            else:
                st.error("⚠ Você precisa selecionar 'Sim' em ambas as confirmações para prosseguir!")
                
    st.markdown("---")

else:
    # ==========================================
    # FLUXO 2: PAINEL PRINCIPAL DE PEDIDOS E VALIDAÇÃO
    # ==========================================
    st.subheader("📋 PEDIDOS DE LPN")

    col_tit_painel, col_btn_att = st.columns([5, 1.5])
    with col_tit_painel:
        st.markdown("### Selecione o pedido abaixo para iniciar:")
    
    with col_btn_att:
        gif_base64 = ""
        if os.path.exists(IMAGENS["att_gif"]):
            with open(IMAGENS["att_gif"], "rb") as f:
                gif_base64 = base64.b64encode(f.read()).decode()

        st.markdown(f"""
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
        """, unsafe_allow_html=True)

        query_params = st.query_params
        if "atualizar_pedidos" in query_params:
            st.query_params.clear()
            st.cache_data.clear()
            st.rerun()

    mapa_pedidos = {}
    if dados_validos:
        pedidos_pendentes = [r for r in dados_validos if not (len(r) > 13 and r[13].strip())]
        if pedidos_pendentes:
            num_colunas = 6
            linhas_cards = [pedidos_pendentes[i:i + num_colunas] for i in range(0, len(pedidos_pendentes), num_colunas)]
            for bloco in linhas_cards:
                cols = st.columns(num_colunas)
                for i, r in enumerate(bloco):
                    idx_p = dados_validos.index(r) + 1
                    linha_real = registos.index(r) + 1
                    try:
                        linha_pedido = r[1] if len(r) > 1 else ""
                        cod_material = r[7] if len(r) > 7 else ""
                        desc_completa = r[2] if len(r) > 2 else ""
                        desc_resumida = (desc_completa[:22] + "...") if len(desc_completa) > 22 else desc_completa
                        data_palete = r[3] if len(r) > 3 else ""
                        data_vencimento = r[9] if len(r) > 9 else ""
                        lote = r[10] if len(r) > 10 else ""
                        lpn_inteira = r[4] if len(r) > 4 else "0"
                        quebra_txt = r[6] if len(r) > 6 else "0"
                        total_esperado = obter_quantidade_total_lpns(r)
                        e_prioridade = len(pedidos_pendentes) > 5
                        lpns_ja_lidas = st.session_state.lpns_validadas_por_pedido.get(idx_p, [])
                        qtd_lidas = len(lpns_ja_lidas)
                        porcentagem = min(int((qtd_lidas / total_esperado) * 100), 100)
                        
                        mapa_pedidos[idx_p] = {"num_pedido": idx_p, "linha": linha_real, "registro": r, "total_esperado": total_esperado}
                        
                        with cols[i]:
                            is_selecionado = (st.session_state.pedido_selecionado_idx == idx_p)
                            classe_card = "card-pedido" if (is_selecionado or not e_prioridade) else "card-pedido-prioridade"
                            destaque_sel = "border: 2px solid #00bfff; background-color: #16222b;" if is_selecionado else ""
                            tag_prioridade_html = '<span style="color: #ff4b4b; font-weight: bold;">🔴 URGENTE / PRIORIDADE</span><br>' if e_prioridade else ''
                            
                            st.markdown(f"""<div class="{classe_card}" style="{destaque_sel}">
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
<span style="color: #00bfff;"><b>Progresso: {qtd_lidas}/{total_esperado} ({porcentagem}%)</b></span>
</div>""", unsafe_allow_html=True)
                            
                            label_botao_card = "✔ Selecionado" if is_selecionado else f"Selecionar Pedido {idx_p}"
                            if st.button(label_botao_card, key=f"btn_sel_{idx_p}", use_container_width=True):
                                st.session_state.pedido_selecionado_idx = idx_p
                                st.rerun()
                    except Exception:
                        continue
        else:
            st.success("🎉 Todos os pedidos já foram validados e concluídos!")
    else:
        st.info("Nenhuma solicitação encontrada na planilha.")

    st.markdown("---")

    # ==========================================
    # SEÇÃO INFERIOR: FORMULÁRIO E VALIDAÇÃO DE CÓDIGOS
    # ==========================================
    st.subheader("📝 Validar e Dar Baixa na LPN")
    
    col_form, col_img, col_acao = st.columns([1.1, 1.2, 1.2], gap="large")
    
    with col_form:
        nome_responsavel = st.text_input("Nome", value=st.session_state.val_nome, placeholder="Digite seu nome...", key="input_nome_field")
        st.session_state.val_nome = nome_responsavel
        
        bc1 = st.text_input("1º Código de Barras (LPN)", value=st.session_state.val_bc1, key="input_bc1_field")
        st.session_state.val_bc1 = bc1
        bc2 = st.text_input("2º Código de Barras", value=st.session_state.val_bc2, key="input_bc2_field")
        st.session_state.val_bc2 = bc2
        bc3 = st.text_input("3º Código de Barras", value=st.session_state.val_bc3, key="input_bc3_field")
        st.session_state.val_bc3 = bc3

        idx_sel_atual = st.session_state.get("pedido_selecionado_idx")
        if idx_sel_atual and idx_sel_atual in mapa_pedidos:
            p_info = mapa_pedidos[idx_sel_atual]
            lidas_atualmente = st.session_state.lpns_validadas_por_pedido.get(p_info["num_pedido"], [])
            tot_esperado_pedido = p_info["total_esperado"]
            qtd_lidas = len(lidas_atualmente)
            porcentagem_calc = min(int((qtd_lidas / tot_esperado_pedido) * 100), 100)
            st.markdown(f"**Progresso:** {qtd_lidas} de {tot_esperado_pedido} LPNs ({porcentagem_calc}%)")
            st.progress(porcentagem_calc / 100.0)

    with col_img:
        st.markdown('<div class="container-coluna-meio">', unsafe_allow_html=True)
        
        erro = st.session_state.get("erro_ativo")
        det = st.session_state.get("detalhes_erro", {"solicitado": "", "lido": ""})
        if erro == "material04":
            st.markdown('<div class="alerta-piscar">🚫 Erro no Material</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">Incompatível com o solicitado.</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao"><b>SOLICITADO:</b> {det['solicitado']}<br><b>Gerado na LPN:</b> {det['lido']}</div>""", unsafe_allow_html=True)
            if os.path.exists(IMAGENS["material04"]): st.image(IMAGENS["material04"], width=310)
        elif erro == "lote06":
            st.markdown('<div class="alerta-piscar">🚫 Erro de Lote</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">Imcompatível com a data de vencimento.</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao"><b>SOLICITADO:</b> {det['solicitado']}<br><b>Gerado na LPN:</b> {det['lido']}</div>""", unsafe_allow_html=True)
            if os.path.exists(IMAGENS["lote06"]): st.image(IMAGENS["lote06"], width=310)
        elif erro == "datav02":
            st.markdown('<div class="alerta-piscar">🚫 Erro de Data de Validade</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">Data de vencimento não está compatível.</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao"><b>SOLICITADO:</b> {det['solicitado']}<br><b>Gerado na LPN:</b> {det['lido']}</div>""", unsafe_allow_html=True)
            if os.path.exists(IMAGENS["datav02"]): st.image(IMAGENS["datav02"], width=310)
        elif erro == "datafab03":
            st.markdown('<div class="alerta-piscar">🚫 Erro de Data de Fabricação</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">Data de fabricação não está de acordo.</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao"><b>SOLICITADO:</b> {det['solicitado']}<br><b>Gerado na LPN:</b> {det['lido']}</div>""", unsafe_allow_html=True)
            if os.path.exists(IMAGENS["datafab03"]): st.image(IMAGENS["datafab03"], width=310)
        elif erro == "dun03":
            st.markdown('<div class="alerta-piscar">🚫 Erro de DUN</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">DUN não corresponde ao solicitado.</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao"><b>SOLICITADO:</b> {det['solicitado']}<br><b>Gerado na LPN:</b> {det['lido']}</div>""", unsafe_allow_html=True)
            if os.path.exists(IMAGENS["dun03"]): st.image(IMAGENS["dun03"], width=310)
        elif erro == "validacao_qtd":
            st.markdown('<div class="alerta-piscar">🚫 Erro de Quantidade / Quebra</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">Quantidade lida não confere com as quebras pendentes.</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao">{det['solicitado']}</div>""", unsafe_allow_html=True)
            if os.path.exists(IMAGENS["validacao_qtd"]): st.image(IMAGENS["validacao_qtd"], width=310)
        elif erro == "lpn_duplicada":
            st.markdown('<div class="alerta-piscar">🚫 LPN Duplicada</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">Esta LPN já foi validada neste pedido.</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao">{det['lido']}</div>""", unsafe_allow_html=True)
            if os.path.exists(IMAGENS["lpn_duplicada"]): st.image(IMAGENS["lpn_duplicada"], width=310)
        elif erro == "limite":
            st.markdown('<div class="alerta-piscar">🚫 Limite Excedido</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">Todas as LPNs deste pedido já foram validas.</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao"><b>INFO:</b> {det['solicitado']}</div>""", unsafe_allow_html=True)
        else:
            if os.path.exists(IMAGENS["guia05"]):
                st.image(IMAGENS["guia05"], width=450)
            elif os.path.exists("image_51919d.png"):
                st.image("image_51919d.png", width=450)
                
        st.markdown('</div>', unsafe_allow_html=True)

    with col_acao:
        st.markdown('<div class="container-coluna-direita">', unsafe_allow_html=True)

        idx_sel_atual = st.session_state.get("pedido_selecionado_idx")
        if not idx_sel_atual or idx_sel_atual not in mapa_pedidos:
            st.markdown("""
            <div style="display: flex; justify-content: center; width: 100%;">
                <div style="background-color: rgba(60, 20, 20, 0.6); border: 2px dashed #ff4b4b; padding: 16px 20px; border-radius: 8px; margin-bottom: 15px; text-align: center; width: 100%; box-sizing: border-box;">
                    <span style="color: #ff4b4b; font-size: 18px; font-weight: bold;">⚠ Para iniciar, por favor selecione um pedido.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            p_sel = mapa_pedidos[idx_sel_atual]
            mat_s = p_sel["registro"][7] if len(p_sel["registro"]) > 7 else "N/D"
            linha_s = p_sel["registro"][1] if len(p_sel["registro"]) > 1 else "N/D"
            st.markdown(f"""
            <div style="display: flex; justify-content: center; width: 100%;">
                <div style="background-color: #152c1a; border: 1px solid #52b788; padding: 12px 16px; border-radius: 8px; margin-bottom: 15px; text-align: center; width: 100%; box-sizing: border-box;">
                    <span style="color: #52b788; font-size: 14px; font-weight: bold;">🎯 Pedido Selecionado:</span><br>
                    <span style="color: #ffffff; font-size: 13px;">Pedido {idx_sel_atual} (Linha: {linha_s} - Mat: {mat_s})</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        validar_img_base64 = ""
        if os.path.exists(IMAGENS["validar_btn"]):
            with open(IMAGENS["validar_btn"], "rb") as f:
                validar_img_base64 = base64.b64encode(f.read()).decode()

        st.markdown('<div class="container-botao-imagem">', unsafe_allow_html=True)
        
        btn_validar_clicado = False
        if validar_img_base64:
            st.markdown(f"""
            <form action="" method="get">
                <button type="submit" name="executar_validacao" value="true" style="
                    background: none;
                    border: none;
                    padding: 0;
                    cursor: pointer;
                    margin: 0 auto;
                ">
                    <img src="data:image/png;base64,{validar_img_base64}" width="240px" class="btn-neon-img">
                </button>
            </form>
            """, unsafe_allow_html=True)
            
            if "executar_validacao" in st.query_params:
                st.query_params.clear()
                btn_validar_clicado = True
        else:
            st.warning("⚠️ Imagem 'validar.png' não encontrada na pasta. Usando botão padrão de texto.")
            btn_validar_clicado = st.button("VALIDAR LPN", key="btn_validar_lpn_fallback", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Processamento das regras de validação ao clicar no botão
        if btn_validar_clicado:
            bc1_val = st.session_state.get("val_bc1", "").strip()
            bc2_val = st.session_state.get("val_bc2", "").strip()
            bc3_val = st.session_state.get("val_bc3", "").strip()
            
            if not nome_responsavel.strip():
                st.warning("⚠ Digite o seu nome.")
                st.stop()
            idx_sel = st.session_state.get("pedido_selecionado_idx")
            if not idx_sel or idx_sel not in mapa_pedidos:
                st.warning("⚠ Para iniciar, por favor selecione um pedido.")
                st.stop()
            if not bc1_val or not bc2_val or not bc3_val:
                st.warning("⚠ Preencha os 3 códigos de barras.")
                st.stop()
                
            lpn_lida = processar_codigo_1(bc1_val)
            mat_lido, qtd_lida, lote_lido = processar_codigo_2(bc2_val)
            dun_lido, venc_lido, fab_lido = processar_codigo_3(bc3_val)
            
            info_pedido = mapa_pedidos[idx_sel]
            linha_encontrada = info_pedido["linha"]
            num_pedido_escolhido = info_pedido["num_pedido"]
            r_escolhido = info_pedido["registro"]
            total_necessario = info_pedido["total_esperado"]
            lpns_ja_lidas = st.session_state.lpns_validadas_por_pedido.get(num_pedido_escolhido, [])

            if lpn_lida in lpns_ja_lidas:
                st.session_state.erro_ativo = "lpn_duplicada"
                st.session_state.detalhes_erro = {"solicitado": "", "lido": f"LPN já validada anteriormente: {lpn_lida}"}
                tocar_som_erro()
                st.rerun()

            qtd_inteira_esperada = obter_quantidade_inteira(r_escolhido)
            lista_quebras = obter_lista_quebras(r_escolhido)
            
            # Validação do material
            mat_esperado = limpar_texto(r_escolhido[7]) if len(r_escolhido) > 7 else ""
            if mat_lido and mat_esperado and mat_lido != mat_esperado:
                st.session_state.erro_ativo = "material04"
                st.session_state.detalhes_erro = {"solicitado": mat_esperado, "lido": mat_lido}
                tocar_som_erro()
                st.rerun()

            # Validação do DUN
            dun_esperado = limpar_texto(r_escolhido[8]) if len(r_escolhido) > 8 else ""
            if dun_lido and dun_esperado and dun_lido != dun_esperado:
                st.session_state.erro_ativo = "dun03"
                st.session_state.detalhes_erro = {"solicitado": dun_esperado, "lido": dun_lido}
                tocar_som_erro()
                st.rerun()

            # Validação de Data de Vencimento
            venc_esperado_str = r_escolhido[9] if len(r_escolhido) > 9 else ""
            data_venc_obj = converter_para_data_obj(venc_esperado_str)
            if venc_lido and data_venc_obj:
                data_lida_venc = converter_para_data_obj(venc_lido)
                if data_lida_venc and data_lida_venc != data_venc_obj:
                    st.session_state.erro_ativo = "datav02"
                    st.session_state.detalhes_erro = {"solicitado": data_venc_obj.strftime("%d/%m/%Y"), "lido": data_lida_venc.strftime("%d/%m/%Y")}
                    tocar_som_erro()
                    st.rerun()

            # Validação de Lote
            lote_esperado = limpar_texto(r_escolhido[10]) if len(r_escolhido) > 10 else ""
            if lote_lido and lote_esperado and lote_lido != lote_esperado:
                st.session_state.erro_ativo = "lote06"
                st.session_state.detalhes_erro = {"solicitado": lote_esperado, "lido": lote_lido}
                tocar_som_erro()
                st.rerun()

            # Passou pelas validações básicas, ativa a tela de confirmação visual
            st.session_state.erro_ativo = None
            st.session_state.etapa_validacao = True
            st.session_state.dados_conferencia = {
                "num_pedido": num_pedido_escolhido,
                "linha": linha_encontrada,
                "lpn": lpn_lida,
                "descricao": r_escolhido[2] if len(r_escolhido) > 2 else "N/D",
                "responsavel": nome_responsavel.strip(),
                "total_esperado": total_necessario
            }
            st.rerun()
