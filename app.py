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

# Dicionario com os arquivos de imagem usados na interface
IMAGENS = {
    "guia05": "GUIA DE CODIGO DE LPN.JPG",
    "conf_desc": "descricao material.png",
    "conf_ordem": "ordemdeprod.png",
    "material04": "ERRO NO MATERIAL - INCOMPATIVEL COM O SOLICITADO.png",
    "lote06": "LOTE IMCOMPATIVEL COM LA DATA DE VENCIMENTO.png" if "LOTE IMCOMPATIVEL COM LA DATA DE VENCIMENTO.png" else "lote06.png",
    "datav02": "DATA DE VENCIMENTO NAO ESTA COMPATIVEL.png",
    "datafab03": "DATA DE FABRICAÇÃO NAO ESTA DE ACORDO COM O SOLICITADO.png",
    "dun03": "DUN NAO ESTA CORRESPONDENTE A DUN DO MATERIAL SOLICITADO.png",
    "validacao_qtd": "validação da quantidade.PNG",
    "lpn_duplicada": "lpnduplicada.PNG",  # Sua imagem de LPN duplicada integrada
    "sonic_gif": "sonicgif/SONICGIF.gif",
}

# Configuração inicial da pagina do aplicativo
st.set_page_config(page_title="Validação de LPN", page_icon="📦", layout="wide")

# Atualiza a pagina automaticamente a cada 3 minutos
count = st_autorefresh(interval=180000, key="datarefresh")

# Estilos visuais em CSS e o script pra rolar a tela automaticamente
st.markdown("""
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

# Funcao para tocar o som de erro
def tocar_som_erro():
    sound_html = """
        <audio autoplay>
            <source src="https://assets.mixkit.co/active_storage/sfx/2575/2575-preview.mp3" type="audio/mpeg">
        </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# Conexao com a planilha do Google Sheets
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

# Funcoes auxiliares de tratamento de texto e datas
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

st.markdown("## 📦 Validação das informações das Lpn")

# Inicializacao de estados
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

registos, dados_validos = [], []
try:
    registos = sheet.get_all_values()
    if len(registos) > 1:
        for r in registos[1:]:
            if any(str(celula).strip() for celula in r):
                dados_validos.append(r)
except Exception as e:
    st.warning(f"Aviso ao carregar dados da planilha: {e}")
    # Coleta de pedidos pendentes para exibicao
pedidos_pendentes = []
for idx, r in enumerate(dados_validos):
    status = str(r[7]).strip().upper() if len(r) > 7 else ""
    if status != "CONCLUIDO":
        pedidos_pendentes.append((idx + 2, r))

# Divisao da tela principal em colunas
col_esq, col_dir = st.columns([1.2, 1])

with col_esq:
    st.markdown("### 📋 Pedidos Pendentes")
    if not pedidos_pendentes:
        st.success("🎉 Todos os pedidos foram concluídos!")
    else:
        for idx_planilha, r in pedidos_pendentes:
            nome_cliente = str(r[0]).strip() if len(r) > 0 else ""
            material_ped = str(r[1]).strip() if len(r) > 1 else ""
            qtd_ped = str(r[4]).strip() if len(r) > 4 else ""
            prioridade = str(r[8]).strip().upper() if len(r) > 8 else ""
            
            is_selecionado = (st.session_state.pedido_selecionado_idx == idx_planilha)
            borda_extra = "border: 3px solid #ffffff;" if is_selecionado else ""
            
            if prioridade == "SIM":
                css_card = "card-pedido-prioridade"
                tag_prio = "🔥 **URGENTE / PRIORIDADE**<br>"
            else:
                css_card = "card-pedido"
                tag_prio = ""
                
            card_html = f"""
                <div class="{css_card}" style="{borda_extra}">
                    {tag_prio}
                    <b>Cliente/LPN:</b> {nome_cliente}<br>
                    <b>Material:</b> {material_ped}<br>
                    <b>Qtd:</b> {qtd_ped} | <b>Linha:</b> {idx_planilha}
                </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(f"Selecionar Linha {idx_planilha}", key=f"sel_{idx_planilha}"):
                st.session_state.pedido_selecionado_idx = idx_planilha
                st.session_state.etapa_validacao = True
                if len(r) > 0: st.session_state.val_nome = str(r[0]).strip()
                st.rerun()

    st.markdown('<div id="secao-validacao"></div>', unsafe_allow_html=True)
    
    if st.session_state.etapa_validacao and st.session_state.pedido_selecionado_idx:
        st.markdown("---")
        st.markdown(f"### 🔍 Validando Pedido (Linha {st.session_state.pedido_selecionado_idx})")
        
        linha_atual = None
        for idx_p, r in pedidos_pendentes:
            if idx_p == st.session_state.pedido_selecionado_idx:
                linha_atual = r
                break
                
        if linha_atual:
            sol_nome = str(linha_atual[0]).strip()
            sol_mat = str(linha_atual[1]).strip()
            sol_ordem = str(linha_atual[2]).strip()
            sol_lote = str(linha_atual[3]).strip()
            sol_qtd = str(linha_atual[4]).strip()
            sol_venc = str(linha_atual[5]).strip()
            
            st.markdown(f"**LPN / Cliente:** <span class='texto-destaque-lpn'>{sol_nome}</span>", unsafe_allow_html=True)
            st.markdown(f"**Material Solicitado:** <span class='texto-destaque-mat'>{sol_mat}</span>", unsafe_allow_html=True)
            st.markdown(f"**Ordem:** {sol_ordem} | **Lote:** {sol_lote} | **Qtd:** {sol_qtd} | **Vencimento:** {sol_venc}")
            
            with st.form(key="form_validacao_lpn"):
                st.markdown("#### Digite ou Bipe os Códigos de Barras:")
                bc1 = st.text_input("Código 1 (Ex: LPN / EAN / Material)", value=st.session_state.val_bc1)
                bc2 = st.text_input("Código 2 (Ex: Código com Lote e Qtd)", value=st.session_state.val_bc2)
                bc3 = st.text_input("Código 3 (Ex: DUN / Validade / Fabricação)", value=st.session_state.val_bc3)
                
                btn_validar = st.form_submit_button("Validar e Concluir LPN")
                
                if btn_validar:
                    st.session_state.val_bc1 = bc1
                    st.session_state.val_bc2 = bc2
                    st.session_state.val_bc3 = bc3
                    
                    lpn_lida = processar_codigo_1(bc1)
                    
                    # 1. VERIFICAÇÃO DE LPN DUPLICADA (Usa a imagem lpnduplicada.PNG)
                    if not st.session_state.lpns_validadas_por_pedido:
                        st.session_state.lpns_validadas_por_pedido = {}
                    
                    lpns_ja_lidas = st.session_state.lpns_validadas_por_pedido.get(st.session_state.pedido_selecionado_idx, [])
                    
                    if lpn_lida and lpn_lida in lpns_ja_lidas:
                        st.session_state.erro_ativo = "lpn_duplicada"
                        st.session_state.detalhes_erro = {
                            "solicitado": "",
                            "lido": f"LPN já validada anteriormente neste pedido: {lpn_lida}"
                        }
                        tocar_som_erro()
                    else:
                        # Processamento normal dos demais códigos e validações...
                        mat_lido, qtd_lido, lote_lido = processar_codigo_2(bc2)
                        dun_lido, venc_lido_str, fab_lido_str = processar_codigo_3(bc3)
                        
                        venc_lido_formatado = formatar_data_aammdd(venc_lido_str)
                        
                        # Validação de Material
                        if sol_mat and mat_lido and limpar_texto(sol_mat) != limpar_texto(mat_lido):
                            st.session_state.erro_ativo = "material"
                            st.session_state.detalhes_erro = {"solicitado": sol_mat, "lido": mat_lido}
                            tocar_som_erro()
                        else:
                            # Se passou nas validações, registra a LPN como lida com sucesso
                            if lpn_lida:
                                if st.session_state.pedido_selecionado_idx not in st.session_state.lpns_validadas_por_pedido:
                                    st.session_state.lpns_validadas_por_pedido[st.session_state.pedido_selecionado_idx] = []
                                st.session_state.lpns_validadas_por_pedido[st.session_state.pedido_selecionado_idx].append(lpn_lida)
                            
                            st.session_state.erro_ativo = None
                            sheet.update_cell(st.session_state.pedido_selecionado_idx, 8, "CONCLUIDO")
                            st.success("✅ LPN validada e pedido concluído com sucesso!")
                            st.session_state.etapa_validacao = False
                            st.session_state.pedido_selecionado_idx = None
                            st.rerun()

with col_dir:
    st.markdown("### 🚨 Painel de Erros / Alertas")
    
    if st.session_state.erro_ativo:
        erro = st.session_state.erro_ativo
        det = st.session_state.detalhes_erro
        
        if erro == "lpn_duplicada":
            st.markdown('<div class="alerta-piscar">🚫 LPN Duplicada</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao"><b>{det['lido']}</b></div>""", unsafe_allow_html=True)
            img_dup_path = IMAGENS.get("lpn_duplicada", "lpnduplicada.PNG")
            if os.path.exists(img_dup_path):
                st.image(img_dup_path, width=450)
            else:
                st.warning(f"⚠ Imagem `{img_dup_path}` não encontrada na pasta.")
                
        elif erro == "material":
            st.markdown('<div class="alerta-piscar">❌ Erro no Material</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="alerta-comparacao"><b>Solicitado:</b> {det['solicitado']}<br><b>Lido:</b> {det['lido']}</div>""", unsafe_allow_html=True)
            img_path = IMAGENS.get("material04")
            if img_path and os.path.exists(img_path):
                st.image(img_path, width=450)
                
        if st.button("Limpar Erro"):
            st.session_state.erro_ativo = None
            st.rerun()
    else:
        st.info("ℹ️ Nenhum erro ativo no momento. Sistema operando normalmente.")
        sonic_path = IMAGENS.get("sonic_gif")
        if sonic_path and os.path.exists(sonic_path):
            st.image(sonic_path, width=250)

# Rodapé centralizado
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; font-size: 12px;'>Sistema de Validação de LPN &bull; Integrado com Google Sheets</div>", unsafe_allow_html=True)
