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
    "att_gif": "att.gif", # GIF do anel / ícone de atualização
}

# Configura a pagina do streamlit pra usar o layout largo
st.set_page_config(page_title="Validação de LPN", page_icon="📦", layout="wide")

# Dá um refresh automatico na pagina a cada 3 minutos pra pegar dados novos
count = st_autorefresh(interval=180000, key="datarefresh")

# ==========================================
# ESTILOS VISUAIS (CSS) E JAVASCRIPT
# ==========================================
st.markdown("""
    <style>
    /* Remove o espaço em branco excessivo no topo da página do Streamlit */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 5rem !important;
    }
    header[data-testid="stHeader"] {
        background: transparent;
    }
    
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

    /* Estilo personalizado para o botão ATUALIZAR PEDIDOS */
    .stButton > button.btn-atualizar-estilo {
        background-color: #000000 !important;
        border: 2px solid #00bfff !important;
        border-radius: 14px !important;
        color: #00bfff !important;
        font-weight: bold !important;
        font-size: 12px !important;
        padding: 6px 10px !important;
        width: 100% !important;
        box-shadow: 0 0 8px rgba(0, 191, 255, 0.3) !important;
        transition: 0.2s ease-in-out !important;
    }
    .stButton > button.btn-atualizar-estilo:hover {
        background-color: #0c1a24 !important;
        border-color: #3498db !important;
        color: #3498db !important;
        box-shadow: 0 0 12px rgba(52, 152, 219, 0.6) !important;
    }

    /* RODAPÉ FIXO ABSOLUTO NA TELA */
    .footer-fixo {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        background-color: #0e1117 !important;
        border-top: 1px solid #333333 !important;
        padding: 8px 0 !important;
        text-align: center !important;
        z-index: 999999 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 10px !important;
    }
    </style>
    
    <script>
    function rolarParaValidacao() {
        const elemento = document.getElementById('secao-validacao');
        if (elemento) {
            elemento.scrollIntoView({ behavior: 'smooth' });
        }
    }
    setTimeout(rolarParaValidacao, 200);
    </script>
""", unsafe_allow_html=True)

# Função pra tocar o som de erro quando der algo errado
def tocar_som_erro():
    sound_html = """
        <audio autoplay>
            <source src="https://assets.mixkit.co/active_storage/sfx/2575/2575-preview.mp3" type="audio/mpeg">
        </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# ==========================================
# CONEXÃO COM O GOOGLE SHEETS
# ==========================================
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

def formatar_data_aammdd(data_str):
    if not data_str: return data_str
    data_str = re.sub(r'\D', '', str(data_str))
    if len(data_str) != 6: return data_str
    try:
        ano = "20" + data_str[0:2]
        mes = data_str[2:4]
        dia = data_str[4:6]
        datetime(int(ano), int(mes), int(dia))
        return f"{dia}/{mes}/{ano}"
    except Exception:
        return data_str

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
        if match_dun:
            dun = match_dun.group(1)
        else:
            match_dun_alt = re.search(r'02(\d+?)(?=17|11|$)', limpo)
            dun = match_dun_alt.group(1) if match_dun_alt else limpo[2:16]
            
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

# Cabeçalho da pagina (compactado no topo)
st.markdown("## 📦 Validação das informações das Lpn")

# Inicializa as variáveis de controle no session_state se não existirem
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

# Organização do topo com abas e o botão personalizado ao lado
col_abas, col_espaco, col_botao_att = st.columns([5, 0.5, 2])

with col_abas:
    aba_painel, aba_concluidos = st.tabs(["📋 Painel Principal e Validação", "🕒 Concluídos nas Últimas 24h"])

with col_botao_att:
    st.markdown("<div style='margin-top: 2px;'></div>", unsafe_allow_html=True)
    
    # Monta o HTML do botão com o GIF em cima e o texto em azul embaixo
    gif_html = ""
    if os.path.exists(IMAGENS["att_gif"]):
        with open(IMAGENS["att_gif"], "rb") as f:
            encoded_att = base64.b64encode(f.read()).decode()
            gif_html = f'<img src="data:image/gif;base64,{encoded_att}" width="32px" style="display: block; margin: 0 auto 4px auto;">'
    else:
        gif_html = '<span style="font-size: 20px; display: block; text-align: center; margin-bottom: 2px;">🟡</span>'

    html_botao_custom = f"""
    <div style="background-color: #000000; border: 2px solid #00bfff; border-radius: 14px; padding: 6px; text-align: center; box-shadow: 0 0 8px rgba(0, 191, 255, 0.3);">
        {gif_html}
        <span style="color: #00bfff; font-size: 11px; font-weight: bold; font-family: sans-serif; display: block; letter-spacing: 0.5px;">ATUALIZAR PEDIDOS</span>
    </div>
    """
    
    # Botão invisível em cima para capturar o clique do usuário mantendo o layout exato
    if st.button("Atualizar Pedidos", key="btn_atualizar_customizado", use_container_width=True, help="Atualizar dados da planilha"):
        st.cache_data.clear()
        st.rerun()
        
    # Insere o visual estilizado sobrepondo/acompanhando o botão do Streamlit via JS/HTML
    st.markdown(f"""
    <style>
    /* Oculta o texto padrão do botão do Streamlit para exibir apenas o nosso design customizado */
    div[data-testid="column"] button[key="btn_atualizar_customizado"] p {{
        visibility: hidden;
    }}
    div[data-testid="column"] button[key="btn_atualizar_customizado"] {{
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        height: auto !important;
    }}
    div[data-testid="column"] button[key="btn_atualizar_customizado"]::after {{
        content: "";
        display: block;
    }}
    </style>
    <div style="margin-top: -46px; pointer-events: none;">
        {html_botao_custom}
    </div>
    """, unsafe_allow_html=True)

# Pega todos os dados da planilha
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
# CONTEÚDO DA ABA PRINCIPAL
# ==========================================
with aba_painel:
    st.subheader("📋 Painel de Solicitações Pendentes")
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
                            destaque_sel = "border: 2px solid #2ecc71; box-shadow: 0 0 10px #2ecc71;" if is_selecionado else ""
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
<span style="color: #f1c40f;"><b>Progresso: {qtd_lidas}/{total_esperado} ({porcentagem}%)</b></span>
</div>""", unsafe_allow_html=True)
                            
                            label_botao = "✅ Selecionado" if is_selecionado else f"Selecionar Pedido {idx_p}"
                            if st.button(label_botao, key=f"btn_sel_{idx_p}", use_container_width=True):
                                st.session_state.pedido_selecionado_idx = idx_p
                                st.rerun()
                    except Exception:
                        continue
        else:
            st.success("🎉 Todos os pedidos já foram validados e concluídos!")
    else:
        st.info("Nenhuma solicitação encontrada na planilha.")

    st.markdown("---")
    st.markdown('<div id="secao-validacao"></div>', unsafe_allow_html=True)

    # Etapa de confirmação visual obrigatória antes de salvar na planilha
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
                ⚠️ LPNs MERAMENTE ILUSTRATIVAS<br>
                SEUS VALORES DEVEM SER CONSIDERADOS APENAS COMO EXEMPLO PARA FACILITAR A VISUALIZAÇÃO DA DIVERGÊNCIA.
            </div>
            {sonic_html}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f'📦 **LPN Atual:** <span class="texto-destaque-lpn">{d["lpn"]}</span>', unsafe_allow_html=True)
        st.markdown(f'🏷 **Material:** <span class="texto-destaque-mat">{d["descricao"]}</span>', unsafe_allow_html=True)

        col_conf1, col_conf2 = st.columns(2)
        with col_conf1:
            resp_desc_str = st.radio("📌 A descrição está correta?", ["Selecione...", "Sim", "Não"], horizontal=True, key="r_desc")
            if os.path.exists(IMAGENS["conf_desc"]): st.image(IMAGENS["conf_desc"], width=420)
        with col_conf2:
            resp_ordem_str = st.radio("📌 Você verificou a ordem?", ["Selecione...", "Sim", "Não"], horizontal=True, key="r_ordem")
            if os.path.exists(IMAGENS["conf_ordem"]): st.image(IMAGENS["conf_ordem"], width=420)

        if st.button("Confirmar esta LPN", type="primary", use_container_width=True):
            if resp_ordem_str == "Sim" and resp_desc_str == "Sim":
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
                        st.session_state.val_bc1 = st.session_state.val_bc2 = st.session_state.val_bc3 = ""
                        st.cache_data.clear()
                        st.balloons()
                        st.success("🎉 Última LPN confirmada! Pedido concluído com sucesso!")
                        st.rerun()
                    else:
                        st.success(f"✅ LPN `{lpn_atual}` aceita! Restam {total_necessario - len(lpns_lidas_pedido)} LPN(s).")
                        st.session_state.etapa_validacao = False
                        st.session_state.erro_ativo = None
                        st.session_state.dados_conferencia = {}
                        st.session_state.val_bc1 = st.session_state.val_bc2 = st.session_state.val_bc3 = ""
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
            else:
                st.error("⚠ Selecione 'Sim' em ambas as confirmações!")
        st.markdown("---")

    col_form, col_img = st.columns(2)
    with col_form:
        st.subheader("📝 Validar e Dar Baixa na LPN")
        nome_responsavel = st.text_input("Nome", value=st.session_state.val_nome, placeholder="Digite seu nome...", key="input_nome_field")
        st.session_state.val_nome = nome_responsavel
        
        idx_sel_atual = st.session_state.get("pedido_selecionado_idx")
        if idx_sel_atual and idx_sel_atual in mapa_pedidos:
            p_sel = mapa_pedidos[idx_sel_atual]
            mat_s = p_sel["registro"][7] if len(p_sel["registro"]) > 7 else "N/D"
            linha_s = p_sel["registro"][1] if len(p_sel["registro"]) > 1 else "N/D"
            st.markdown(f"🎯 **Pedido Selecionado:** Pedido {idx_sel_atual} (Linha: {linha_s} - Mat: {mat_s})")
        else:
            st.markdown("""<div style="background-color: #3a1515; border: 2px dashed #ff4b4b; padding: 12px; border-radius: 6px; margin-bottom: 12px; text-align: center;"><span style="color: #ff4b4b; font-size: 15px; font-weight: bold;">⚠️ POR FAVOR, SELECIONE UM PEDIDO PARA CONFIRMAR AS LPN</span></div>""", unsafe_allow_html=True)

        def executar_validacao():
            bc1_val = st.session_state.get("val_bc1", "").strip()
            bc2_val = st.session_state.get("val_bc2", "").strip()
            bc3_val = st.session_state.get("val_bc3", "").strip()
            
            if not nome_responsavel.strip():
                st.warning("⚠ Digite o seu nome.")
                return
            idx_sel = st.session_state.get("pedido_selecionado_idx")
            if not idx_sel or idx_sel not in mapa_pedidos:
                st.warning("⚠ Selecione um pedido no painel acima.")
                return
            if not bc1_val or not bc2_val or not bc3_val:
                st.warning("⚠️️ Preencha os 3 códigos de barras.")
                return
                
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
                return

            qtd_inteira_esperada = obter_quantidade_inteira(r_escolhido)
            lista_quebras = obter_lista_quebras(r_escolhido)
            if len(lpns_ja_lidas) >= qtd_inteira_esperada:
                if len(lista_quebras) > 0:
                    if qtd_lida not in lista_quebras:
                        st.session_state.erro_ativo = "validacao_qtd"
                        st.session_state.detalhes_erro = {"solicitado": f"Quebras esperadas pendentes: {lista_quebras}", "lido": ""}
                        tocar_som_erro()
                        return
                else:
                    st.session_state.erro_ativo = "limite"
                    st.session_state.detalhes_erro = {"solicitado": f"Limite Máximo Atingido: {total_necessario} LPNs", "lido": f"Tentativa excedida com a LPN: {lpn_lida}"}
                    tocar_som_erro()
                    return

            mat_planilha = limpar_texto(r_escolhido[7] if len(r_escolhido) > 7 else "")
            lote_planilha = limpar_texto(r_escolhido[10] if len(r_escolhido) > 10 else "")
            data_vencimento_planilha_raw = r_escolhido[9] if len(r_escolhido) > 9 else ""
            data_fabricacao_planilha_raw = r_escolhido[3] if len(r_escolhido) > 3 else ""
            dun_planilha = limpar_texto(r_escolhido[8] if len(r_escolhido) > 8 else "")

            if not mat_lido or mat_lido != mat_planilha:
                st.session_state.erro_ativo = "material04"
                st.session_state.detalhes_erro = {"solicitado": mat_planilha or "(Vazio)", "lido": mat_lido or "(Não identificado)"}
                tocar_som_erro()
                return
            if dun_planilha and dun_lido and dun_lido != dun_planilha:
                st.session_state.erro_ativo = "dun03"
                st.session_state.detalhes_erro = {"solicitado": dun_planilha, "lido": dun_lido}
                tocar_som_erro()
                return
            if lote_planilha and lote_lido and lote_lido != lote_planilha:
                st.session_state.erro_ativo = "lote06"
                st.session_state.detalhes_erro = {"solicitado": lote_planilha, "lido": lote_lido}
                tocar_som_erro()
                return
            if data_vencimento_planilha_raw and venc_lido:
                if converter_para_data_obj(venc_lido) != converter_para_data_obj(data_vencimento_planilha_raw):
                    st.session_state.erro_ativo = "datav02"
                    st.session_state.detalhes_erro = {"solicitado": str(data_vencimento_planilha_raw), "lido": formatar_data_aammdd(venc_lido)}
                    tocar_som_erro()
                    return
            if data_fabricacao_planilha_raw and fab_lido:
                if converter_para_data_obj(fab_lido) != converter_para_data_obj(data_fabricacao_planilha_raw):
                    st.session_state.erro_ativo = "datafab03"
                    st.session_state.detalhes_erro = {"solicitado": str(data_fabricacao_planilha_raw), "lido": formatar_data_aammdd(fab_lido)}
                    tocar_som_erro()
                    return

            st.session_state.erro_ativo = None
            st.session_state.detalhes_erro = {"solicitado": "", "lido": ""}
            st.session_state.dados_conferencia = {
                "linha": linha_encontrada, "num_pedido": num_pedido_escolhido,
                "responsavel": nome_responsavel.strip(), "lpn": lpn_lida,
                "quantidade_extraida": qtd_lida, "descricao": r_escolhido[2] if len(r_escolhido) > 2 else "",
                "total_esperado": total_necessario,
            }
            st.session_state.etapa_validacao = True
            st.rerun()

        bc1 = st.text_input("1º Código de Barras (LPN)", value=st.session_state.val_bc1, key="input_bc1_field")
        st.session_state.val_bc1 = bc1
        bc2 = st.text_input("2º Código de Barras", value=st.session_state.val_bc2, key="input_bc2_field")
        st.session_state.val_bc2 = bc2
        bc3 = st.text_input("3º Código de Barras", value=st.session_state.val_bc3, key="input_bc3_field")
        st.session_state.val_bc3 = bc3

        texto_botao_validar = "Validar LPN"
        if idx_sel_atual and idx_sel_atual in mapa_pedidos:
            p_info = mapa_pedidos[idx_sel_atual]
            lidas_atualmente = st.session_state.lpns_validadas_por_pedido.get(p_info["num_pedido"], [])
            tot_esperado_pedido = p_info["total_esperado"]
            qtd_lidas = len(lidas_atualmente)
            if qtd_lidas > 0: texto_botao_validar = "Validar Próxima LPN"
            porcentagem_calc = min(int((qtd_lidas / tot_esperado_pedido) * 100), 100)
            st.markdown(f"**Progresso:** {qtd_lidas} de {tot_esperado_pedido} LPNs ({porcentagem_calc}%)")
            st.progress(porcentagem_calc / 100.0)

        if st.button(texto_botao_validar, type="primary", use_container_width=True):
            executar_validacao()

    with col_img:
        erro = st.session_state.get("erro_ativo")
        det = st.session_state.get("detalhes_erro", {"solicitado": "", "lido": ""})
        if erro == "material04":
            st.markdown('<div class="alerta-piscar">🚫 Erro no Material</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">Incompatível com o solicitado.</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao"><b>SOLICITADO:</b> {det['solicitado']}<br><b>Gerado na LPN:</b> {det['lido']}</div>""", unsafe_allow_html=True)
            if os.path.exists(IMAGENS["material04"]): st.image(IMAGENS["material04"], width=450)
        elif erro == "lote06":
            st.markdown('<div class="alerta-piscar">🚫 Erro de Lote</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">Imcompatível com a data de vencimento.</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao"><b>SOLICITADO:</b> {det['solicitado']}<br><b>Gerado na LPN:</b> {det['lido']}</div>""", unsafe_allow_html=True)
            if os.path.exists(IMAGENS["lote06"]): st.image(IMAGENS["lote06"], width=450)
        elif erro == "datav02":
            st.markdown('<div class="alerta-piscar">🚫 Erro de Data de Validade</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">Data de vencimento não está compatível.</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao"><b>SOLICITADO:</b> {det['solicitado']}<br><b>Gerado na LPN:</b> {det['lido']}</div>""", unsafe_allow_html=True)
            if os.path.exists(IMAGENS["datav02"]): st.image(IMAGENS["datav02"], width=450)
        elif erro == "datafab03":
            st.markdown('<div class="alerta-piscar">🚫 Erro de Data de Fabricação</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">Data de fabricação não está de acordo.</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao"><b>SOLICITADO:</b> {det['solicitado']}<br><b>Gerado na LPN:</b> {det['lido']}</div>""", unsafe_allow_html=True)
            if os.path.exists(IMAGENS["datafab03"]): st.image(IMAGENS["datafab03"], width=450)
        elif erro == "dun03":
            st.markdown('<div class="alerta-piscar">🚫 Erro de DUN</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">DUN não corresponde ao solicitado.</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao"><b>SOLICITADO:</b> {det['solicitado']}<br><b>Gerado na LPN:</b> {det['lido']}</div>""", unsafe_allow_html=True)
            if os.path.exists(IMAGENS["dun03"]): st.image(IMAGENS["dun03"], width=450)
        elif erro == "lpn_duplicada":
            st.markdown('<div class="alerta-piscar">🚫 LPN Duplicada</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao"><b>{det['lido']}</b></div>""", unsafe_allow_html=True)
            img_dup_path = IMAGENS["lpn_duplicada"]
            if os.path.exists(img_dup_path): st.image(img_dup_path, width=450)
            else: st.warning(f"⚠ Imagem `{img_dup_path}` não encontrada na pasta.")
        elif erro in ["validacao_qtd", "limite"]:
            st.markdown('<div class="alerta-piscar">🚫 Validação de Quantidade / LPN</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">LPN\'s inteiras desse pedido já foram validadas.</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao"><b>SOLICITADO:</b> {det['solicitado']}</div>""", unsafe_allow_html=True)
            if os.path.exists(IMAGENS["validacao_qtd"]): st.image(IMAGENS["validacao_qtd"], width=450)
        else:
            st.subheader("💡 Exemplo de LPN")
            if os.path.exists(IMAGENS["guia05"]): st.image(IMAGENS["guia05"], width=450)
            else: st.warning(f"⚠ Imagem `{IMAGENS['guia05']}` não encontrada.")

# ==========================================
# CONTEÚDO DA ABA DE CONCLUÍDOS
# ==========================================
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
                    data_limpa = re.sub(r'\s*\(.*?\)', '', data_str).strip()
                    data_conclusao = datetime.strptime(data_limpa, "%d/%m/%Y %H:%M:%S")
                    data_conclusao = fuso_horario.localize(data_conclusao)
                    if (agora - data_conclusao) <= timedelta(hours=24):
                        concluidos_recentes.append((r, data_limpa))
            except Exception:
                continue
        if concluidos_recentes:
            num_colunas = 6
            linhas_cards_conc = [concluidos_recentes[i:i + num_colunas] for i in range(0, len(concluidos_recentes), num_colunas)]
            for bloco in linhas_cards_conc:
                cols = st.columns(num_colunas)
                for i, (r, data_str) in enumerate(bloco):
                    linha_pedido = r[1] if len(r) > 1 else ""
                    cod_material = r[7] if len(r) > 7 else ""
                    desc_completa_c = r[2] if len(r) > 2 else ""
                    desc_resumida_c = (desc_completa_c[:22] + "...") if len(desc_completa_c) > 22 else desc_completa_c
                    data_palete = r[3] if len(r) > 3 else ""
                    data_vencimento = r[9] if len(r) > 9 else ""
                    lote = r[10] if len(r) > 10 else ""
                    lpn_inteira = r[4] if len(r) > 4 else "0"
                    quebra_txt = r[6] if len(r) > 6 else "0"
                    responsavel = r[11] if len(r) > 11 else "N/D"
                    with cols[i]:
                        st.markdown(f"""<div class="card-concluido"><b>Linha:</b> {linha_pedido}<br><b>Cód Mat:</b> {cod_material}<br><b>Desc:</b> {desc_resumida_c}<br><b>Data Palete:</b> {data_palete}<br><b>Venc:</b> {data_vencimento}<br><b>Lote:</b> {lote}<br><b>LPN Inteira:</b> {lpn_inteira}<br><b>Quebras:</b> {quebra_txt}<br><hr style="margin: 6px 0; border-color: #444; border-width: 1px 0 0 0;"><b>Resp:</b> {responsavel}<br><span style="font-size: 11px; color: #aaaaaa;">🕒 {data_str}</span></div>""", unsafe_allow_html=True)
        else:
            st.info("Nenhum pedido concluído nas últimas 24 horas.")
    else:
        st.info("Nenhum dado encontrado.")

# ==========================================
# RODAPÉ FIXO NA BASE DA TELA
# ==========================================
caminho_meu_gif = "sonicrodape.gif"
if os.path.exists(caminho_meu_gif):
    with open(caminho_meu_gif, "rb") as f:
        encoded_r = base64.b64encode(f.read()).decode()
        sonic_rodape_html = f'<img src="data:image/gif;base64,{encoded_r}" width="35px" style="vertical-align: middle;">'
else:
    sonic_rodape_html = '<span style="font-size: 18px;">🦔💨</span>'

st.markdown(f"""
    <div class="footer-fixo">
        {sonic_rodape_html}
        <span style="color: #f1c40f; font-size: 14px; font-weight: bold; font-family: sans-serif;">Validação de Lpn a todo vapor!</span>
    </div>
""", unsafe_allow_html=True)
