from datetime import datetime
import os
import re
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import pytz
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Configurando a página do app (deixando com visual limpo e moderno)
st.set_page_config(
    page_title="Validação de LPN", page_icon="📦", layout="wide"
)

# Atualiza a página sozinho a cada 3 minutos pra não deixar o painel desatualizado
count = st_autorefresh(interval=180000, key="datarefresh")

# CSS personalizado para o efeito de alerta piscando na tela quando der BO
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
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Conectando com o Google Sheets usando os secrets do Streamlit (sem dor de cabeça)
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
    # Pega direto a aba de solicitações da planilha
    sheet = client.open(spreadsheet_name).worksheet("SOLICITAÇÕES")
except Exception as e:
    st.error(f"Erro ao conectar com o Google Sheets: {e}")
    st.stop()


# --- FUNÇÕES PRA LIMPAR E TRATAR OS DADOS ---
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
    digitos = re.sub(r"\D", "", data_str)
    if len(data_str) == 6 and "/" not in data_str and "-" not in data_str:
        try:
            ano = int("20" + data_str[0:2])
            mes = int(data_str[2:4])
            dia = int(data_str[4:6])
            return datetime(ano, mes, dia).date()
        except Exception:
            pass

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


# Funções pra quebrar os códigos de barras que o leitor bipar na operação
def processar_codigo_1(barcode):
    return barcode.replace("(", "").replace(")", "").strip()


def processar_codigo_2(barcode):
    try:
        limpo = barcode.replace("(", "").replace(")", "")
        match_mat = re.search(r"90(\d+?)(?=37|$)", limpo)
        mat = match_mat.group(1) if match_mat else limpo[2:10]

        match_lote = re.search(r"10(\d+)", limpo)
        if match_lote:
            bloco_lote = match_lote.group(1)
            lote = bloco_lote.lstrip("0") or bloco_lote
        else:
            lote = ""

        return limpar_texto(mat), limpar_texto(lote)[:7]
    except Exception:
        return "", ""


def processar_codigo_3(barcode):
    try:
        limpo = barcode.replace("(", "").replace(")", "")
        match_dun = re.search(r"02(\d+?)(?=17|$)", limpo)
        dun = match_dun.group(1) if match_dun else limpo[2:16]

        match_venc = re.search(r"17(\d{6})", limpo)
        vencimento = (
            formatar_data_aammdd(match_venc.group(1)) if match_venc else ""
        )

        digitos_limpos = re.sub(r"\D", "", limpo)
        data_palete = (
            formatar_data_aammdd(digitos_limpos[-6:])
            if len(digitos_limpos) >= 6
            else ""
        )

        return limpar_texto(dun), limpar_texto(vencimento), limpar_texto(data_palete)
    except Exception:
        return "", "", ""


def obter_quantidade_total_lpns(r):
    try:
        val_e = (
            int(re.sub(r"\D", "", str(r[4])))
            if len(r) > 4 and str(r[4]).strip()
            else 0
        )
    except Exception:
        val_e = 0
    try:
        val_f = (
            int(re.sub(r"\D", "", str(r[5])))
            if len(r) > 5 and str(r[5]).strip()
            else 0
        )
    except Exception:
        val_f = 0
    total = val_e + val_f
    return total if total > 0 else 1


# --- MONTAGEM DA TELA DO APP ---
st.markdown("## 📦 Validação das informações das Lpn")

if "etapa_validacao" not in st.session_state:
    st.session_state.etapa_validacao = False
    st.session_state.dados_conferencia = {}

if "lpns_validadas_por_pedido" not in st.session_state:
    st.session_state.lpns_validadas_por_pedido = {}

if "erro_ativo" not in st.session_state:
    st.session_state.erro_ativo = None

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
    if dados_validos:
        pedidos_pendentes = [
            r for r in dados_validos if not (len(r) > 11 and r[11].strip())
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
                    try:
                        idx_linha = registos.index(r) + 1
                        lpn_col_b = r[1] if len(r) > 1 and r[1].strip() else f"#{idx_linha}"
                        material = r[7] if len(r) > 7 else "N/D"
                        total_esperado = obter_quantidade_total_lpns(r)
                        lpns_ja_lidas = st.session_state.lpns_validadas_por_pedido.get(
                            idx_p, []
                        )
                        qtd_lidas = len(lpns_ja_lidas)
                        porcentagem = min(int((qtd_lidas / total_esperado) * 100), 100)

                        with cols[i]:
                            st.markdown(
                                f"""
                                    <div style="background-color: #1e1e1e; border: 1px solid #333333; padding: 6px; border-radius: 6px; font-size: 10px; color: #ffffff; margin-bottom: 4px; text-align: center; width: 100%;">
                                        <b style="color: #f1c40f;">Ped. {idx_p}</b><br>
                                        <b>Ref:</b> {lpn_col_b}<br>
                                        <b>Mat:</b> {material}<br>
                                        <span style="color: #f1c40f;"><b>{qtd_lidas}/{total_esperado} ({porcentagem}%)</b></span>
                                    </div>
                                    """,
                                unsafe_allow_html=True,
                            )
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
        st.success(
            f"✔ Validando LPN para o **Pedido {d['num_pedido']}** (Linha {d['linha']}"
            " da planilha)!"
        )
        st.markdown(f"📦 **LPN Atual:** `{d['lpn']}`")
        st.markdown(f"🏷 **Material:** `{d['descricao']}`")

        col_conf1, col_conf2 = st.columns(2)
        with col_conf1:
            if os.path.exists("POR FAVOR VERIFIQUE SE A DESCRIÇÃO DO MATERIAL ESTÁ DE ACORDO COM A SU.png"):
                st.image("POR FAVOR VERIFIQUE SE A DESCRIÇÃO DO MATERIAL ESTÁ DE ACORDO COM A SU.png", width=420, caption="Ref. Descrição")
        with col_conf2:
            if os.path.exists("POR FAVOR VERIFIQUE SE A ORDEM DE PRODUÇÃO É DO MATERIAL E DA LINHA CORRESPONDENTE AO PEDIDO.png"):
                st.image("POR FAVOR VERIFIQUE SE A ORDEM DE PRODUÇÃO É DO MATERIAL E DA LINHA CORRESPONDENTE AO PEDIDO.png", width=420, caption="Ref. Ordem")

        resp_desc_str = st.radio(
            "📌 A descrição está correta?",
            ["Selecione...", "Sim", "Não"],
            horizontal=True,
            key="r_desc",
        )
        resp_ordem_str = st.radio(
            "📌 Você verificou a ordem?",
            ["Selecione...", "Sim", "Não"],
            horizontal=True,
            key="r_ordem",
        )

        if st.button("Confirmar esta LPN", type="primary", use_container_width=True):
            if resp_ordem_str == "Sim" and resp_desc_str == "Sim":
                try:
                    linha = d["linha"]
                    num_ped = d["num_pedido"]
                    lpn_atual = d["lpn"]

                    if num_ped not in st.session_state.lpns_validadas_por_pedido:
                        st.session_state.lpns_validadas_por_pedido[num_ped] = []
                    if lpn_atual not in st.session_state.lpns_validadas_por_pedido[num_ped]:
                        st.session_state.lpns_validadas_por_pedido[num_ped].append(
                            lpn_atual
                        )

                    st.success(
                        f"✅ LPN `{lpn_atual}` aceita! Total validadas:"
                        f" {len(st.session_state.lpns_validadas_por_pedido[num_ped])}"
                    )
                    st.session_state.etapa_validacao = False
                    st.session_state.erro_ativo = None
                    if "dados_conferencia" in st.session_state:
                        del st.session_state.dados_conferencia
                    
                    for k in ["input_bc1", "input_bc2", "input_bc3"]:
                        if k in st.session_state:
                            del st.session_state[k]
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

        opcoes_pedidos = ["Selecione o pedido..."]
        mapa_pedidos = {}
        if dados_validos:
            for idx_p, r in enumerate(dados_validos, start=1):
                responsavel_atual = r[11] if len(r) > 11 else ""
                if not responsavel_atual.strip():
                    mat_txt = r[7] if len(r) > 7 else "N/D"
                    tot_esp = obter_quantidade_total_lpns(r)
                    label_ped = (
                        f"Pedido {idx_p} - Mat: {mat_txt} (Esperado: {tot_esp} LPNs)"
                    )
                    opcoes_pedidos.append(label_ped)
                    linha_real = registos.index(r) + 1
                    mapa_pedidos[label_ped] = {
                        "num_pedido": idx_p,
                        "linha": linha_real,
                        "registro": r,
                        "total_esperado": tot_esp,
                    }

        pedido_selecionado = st.selectbox(
            "📌 Selecione o Número do Pedido", opcoes_pedidos
        )

        def executar_validacao():
            bc1_val = st.session_state.get("input_bc1", "").strip()
            bc2_val = st.session_state.get("input_bc2", "").strip()
            bc3_val = st.session_state.get("input_bc3", "").strip()

            if not nome_responsavel.strip():
                st.warning("⚠️ Digite o seu nome.")
                return
            if pedido_selecionado == "Selecione o pedido...":
                st.warning("⚠️ Selecione o pedido.")
                return
            if not bc1_val or not bc2_val or not bc3_val:
                st.warning("⚠️️ Preencha os 3 códigos de barras.")
                return

            lpn_lida = processar_codigo_1(bc1_val)
            mat_lido, lote_lido = processar_codigo_2(bc2_val)
            dun_lido, venc_lido, palete_lido = processar_codigo_3(bc3_val)

            info_pedido = mapa_pedidos[pedido_selecionado]
            linha_encontrada = info_pedido["linha"]
            num_pedido_escolhido = info_pedido["num_pedido"]
            r_escolhido = info_pedido["registro"]
            total_necessario = info_pedido["total_esperado"]

            lpns_ja_lidas = st.session_state.lpns_validadas_por_pedido.get(
                num_pedido_escolhido, []
            )
            if len(lpns_ja_lidas) >= total_necessario:
                st.error("❌ Limite de LPNs atingido para este pedido!")
                st.session_state.erro_ativo = "limite"
                return
            elif lpn_lida in lpns_ja_lidas:
                st.error("❌ Esta LPN já foi validada neste pedido!")
                st.session_state.erro_ativo = "lpn_duplicada"
                return

            mat_planilha = limpar_texto(r_escolhido[7] if len(r_escolhido) > 7 else "")
            lote_planilha = limpar_texto(
                r_escolhido[10] if len(r_escolhido) > 10 else ""
            )
            data_planilha_raw = r_escolhido[9] if len(r_escolhido) > 9 else ""
            dun_planilha = limpar_texto(r_escolhido[8] if len(r_escolhido) > 8 else "")

            if not mat_lido or mat_lido != mat_planilha:
                st.session_state.erro_ativo = "material"
                return

            if dun_planilha and dun_lido and dun_lido != dun_planilha:
                st.session_state.erro_ativo = "dun"
                return

            if lote_planilha and lote_lido and lote_lido != lote_planilha:
                st.session_state.erro_ativo = "lote"
                return

            if data_planilha_raw and venc_lido:
                data_obj_planilha = converter_para_data_obj(data_planilha_raw)
                data_obj_lida = converter_para_data_obj(venc_lido)

                if data_obj_planilha and data_obj_lida:
                    if data_obj_lida != data_obj_planilha:
                        st.session_state.erro_ativo = "validade"
                        return

            st.session_state.erro_ativo = None
            st.session_state.dados_conferencia = {
                "linha": linha_encontrada,
                "num_pedido": num_pedido_escolhido,
                "responsavel": nome_responsavel.strip(),
                "lpn": lpn_lida,
                "descricao": r_escolhido[2] if len(r_escolhido) > 2 else "",
            }
            st.session_state.etapa_validacao = True
            st.rerun()

        bc1 = st.text_input(
            "1º Código de Barras (LPN)",
            placeholder="Ex: (00)378911505103650406",
            key="input_bc1",
        )
        bc2 = st.text_input(
            "2º Código de Barras",
            placeholder="Ex: (90)65684949...",
            key="input_bc2",
        )
        bc3 = st.text_input(
            "3º Código de Barras",
            placeholder="Ex: (02)77891150103763...",
            key="input_bc3",
        )

        if pedido_selecionado != "Selecione o pedido...":
            p_info = mapa_pedidos[pedido_selecionado]
            lidas_atualmente = st.session_state.lpns_validadas_por_pedido.get(
                p_info["num_pedido"], []
            )
            tot_esperado_pedido = p_info["total_esperado"]
            qtd_lidas = len(lidas_atualmente)
            porcentagem_calc = min(int((qtd_lidas / tot_esperado_pedido) * 100), 100)
            st.markdown(
                f"**Progresso:** {qtd_lidas} de {tot_esperado_pedido} LPNs"
                f" ({porcentagem_calc}%)"
            )
            st.progress(porcentagem_calc / 100.0)

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Validar Próxima LPN", type="primary", use_container_width=True):
                executar_validacao()
        with col_btn2:
            btn_finalizar_pedido = st.button(
                "Finalizar Pedido Completo", type="secondary", use_container_width=True
            )

    # Lado direito: exibe alertas visuais ou a imagem de exemplo da LPN
    with col_img:
        erro = st.session_state.get("erro_ativo")

        if erro == "material":
            st.markdown('<div class="alerta-piscar">🚫 Erro no Material</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">Incompatível com o solicitado.</div>', unsafe_allow_html=True)
            img_nome = "ERRO NO MATERIAL - INCOMPATIVEL COM O SOLICITADO.png"
            if os.path.exists(img_nome):
                st.image(img_nome, width=450)
            else:
                st.warning(f"⚠️ Imagem `{img_nome}` não encontrada.")

        elif erro == "lote":
            st.markdown('<div class="alerta-piscar">🚫 Erro de Lote</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">Imcompatível com a data de vencimento.</div>', unsafe_allow_html=True)
            img_nome = "LOTE IMCOMPATIVEL COM A DATA DE VENCIMENTO.png"
            if os.path.exists(img_nome):
                st.image(img_nome, width=450)
            else:
                st.warning(f"⚠️ Imagem `{img_nome}` não encontrada.")

        elif erro == "validade":
            st.markdown('<div class="alerta-piscar">🚫 Erro de Validade/Fabricação</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">Data de fabricação não está de acordo com o solicitado.</div>', unsafe_allow_html=True)
            img_nome = "DATA DE FABRICAÇÃO NAO ESTA DE ACORDO COM O SOLICITADO.png"
            if os.path.exists(img_nome):
                st.image(img_nome, width=450)
            else:
                st.warning(f"⚠️ Imagem `{img_nome}` não encontrada.")

        elif erro == "dun":
            st.markdown('<div class="alerta-piscar">🚫 Erro de DUN</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">DUN não está correspondente à DUN do material solicitado.</div>', unsafe_allow_html=True)
            img_nome = "DUN NAO ESTA CORRESPONDENTE A DUN DO MATERIAL SOLICITADO.png"
            if os.path.exists(img_nome):
                st.image(img_nome, width=450)
            else:
                st.warning(f"⚠️ Imagem `{img_nome}` não encontrada.")

        elif erro == "limite" or erro == "lpn_duplicada":
            st.markdown('<div class="alerta-piscar">🚫 Erro de Quantidade / LPN</div>', unsafe_allow_html=True)
            st.markdown('<div class="alerta-sub">Esta LPN já foi lida ou o limite total foi atingido.</div>', unsafe_allow_html=True)
            if os.path.exists("ERRO NO MATERIAL - INCOMPATIVEL COM O SOLICITADO.png"):
                st.image("ERRO NO MATERIAL - INCOMPATIVEL COM O SOLICITADO.png", width=450)

        else:
            st.subheader("💡 Exemplo de LPN")
            if os.path.exists("etiqueta_exemplo.png"):
                st.image("etiqueta_exemplo.png", width=450)
            elif os.path.exists("etiqueta_exemplo.jpg"):
                st.image("etiqueta_exemplo.jpg", width=450)
            else:
                st.warning("⚠️️ Salve a imagem com o nome `etiqueta_exemplo.png` na mesma pasta do script.")

    if btn_finalizar_pedido:
        if pedido_selecionado != "Selecione o pedido...":
            info_pedido = mapa_pedidos[pedido_selecionado]
            num_ped = info_pedido["num_pedido"]
            linha_encontrada = info_pedido["linha"]
            total_necessario = info_pedido["total_esperado"]
            lpns_lidas_pedido = st.session_state.lpns_validadas_por_pedido.get(
                num_ped, []
            )

            if len(lpns_lidas_pedido) < total_necessario:
                st.error("⚠️ Faltam LPNs a serem validadas.")
            else:
                fuso_horario = pytz.timezone("America/Sao_Paulo")
                hora_atual = datetime.now(fuso_horario).strftime("%d/%m/%Y %H:%M:%S")
                todas_lpns_str = ", ".join(lpns_lidas_pedido)

                sheet.update_cell(linha_encontrada, 12, nome_responsavel.strip())
                sheet.update_cell(linha_encontrada, 13, todas_lpns_str)
                sheet.update_cell(linha_encontrada, 14, hora_atual)

                if num_ped in st.session_state.lpns_validadas_por_pedido:
                    del st.session_state.lpns_validadas_por_pedido[num_ped]

                st.session_state.erro_ativo = None
                st.balloons()
                st.success("🎉 Pedido concluído com sucesso!")
                st.rerun()

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
            for r, data_str in concluidos_recentes:
                idx_linha = registos.index(r) + 1
                lpn_col_b = r[1] if len(r) > 1 and r[1].strip() else f"#{idx_linha}"
                material = r[7] if len(r) > 7 else "N/D"
                responsavel = r[11] if len(r) > 11 else "N/D"
                st.markdown(
                    f"""
                        <div style="background-color: #1e1e1e; border: 1px solid #333333; padding: 10px 14px; border-radius: 6px; margin-bottom: 8px; font-size: 13px; color: #ffffff;">
                            <b>📦 LPNs:</b> {lpn_col_b} &nbsp;|&nbsp; <b>Mat:</b> {material} &nbsp;|&nbsp; <b>👤 Resp:</b> {responsavel} &nbsp;|&nbsp; <b>🕒</b> {data_str}
                        </div>
                        """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Nenhum pedido concluído nas últimas 24 horas.")
    else:
        st.info("Nenhum dado encontrado.")

# Rodapé com o Sonic correndo
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
