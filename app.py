import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# Config da página (deixar com cara de app limpo)
st.set_page_config(
    page_title="Validação de LPNs",
    page_icon="📦",
    layout="wide"
)

# -----------------------------------------------------------------------------
# CONEXÃO COM O GOOGLE SHEETS
# -----------------------------------------------------------------------------
# Aqui carrego as credenciais do secret do streamlit e conecto na planilha
@st.cache_resource
def conectar_gsheets():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Pega direto dos secrets configurados no app
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # Abre a planilha pelo nome ou link (aqui tô abrindo pelo nome padrão)
    sheet = client.open("Controle_LPNs_Operacao")
    return sheet

try:
    gc_sheet = conectar_gsheets()
except Exception as e:
    st.error(f"Erro ao conectar com o Google Sheets: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# FUNÇÕES AUXILIARES / LÓGICA DE NEGÓCIO
# -----------------------------------------------------------------------------
# Função pra parsear o código de barras GS1 ou formato padrão que a gente recebe
def interpretar_codigo_barras(codigo):
    # TODO: Ajustar isso aqui se mudar o layout da etiqueta do fornecedor
    dados = {
        "material": "",
        "lote": "",
        "validade": "",
        "lpn": ""
    }
    
    # Limpando espaços extras
    codigo = codigo.strip()
    
    # Lógica simples pra quebrar os identifiers se for padrão GS1-128
    # Exemplo básico (preciso refinar depois com os testes da operação)
    if codigo.startswith("01") and len(codigo) >= 16:
        dados["material"] = codigo[2:16]
    else:
        # Se não for GS1, assume que o código inteiro é o material ou lpn
        dados["lpn"] = codigo

    return dados

# -----------------------------------------------------------------------------
# INTERFACE DO USUÁRIO (UI)
# -----------------------------------------------------------------------------
st.title("📦 Sistema de Conferência e Validação de LPNs")
st.markdown("Ferramenta pra conferir os materiais na expedição/recebimento batendo com a planilha.")

# Sidebar pra navegação rápida ou status
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    aba_selecionada = st.radio("Navegação", ["Conferência", "Consultar Planilha"])
    
    st.markdown("---")
    if st.button("🔄 Recarregar Dados"):
        st.cache_resource.clear()
        st.rerun()

# ABA 1: CONFERÊNCIA
if aba_selecionada == "Conferência":
    st.subheader("Leitor de Código / Entrada de Dados")

    col1, col2 = st.columns(2)
    
    with col1:
        # Input do leitor de código de barras (foca aqui direto)
        input_barcode = st.text_input("Bipagem do Código de Barras", placeholder="Passe o leitor aqui...", key="barcode_input")
        
        if input_barcode:
            info = interpretar_codigo_barras(input_barcode)
            st.success("Código Lido com Sucesso!")
            st.json(info)

    with col2:
        st.info("Dica: Certifique-se de que o cursor está na caixa de texto antes de bipar.")
        
        # Formulário manual caso o leitor falhe
        with st.form("form_manual"):
            st.write("Entrada Manual (Fallback)")
            mat_manual = st.text_input("Material")
            lote_manual = st.text_input("Lote")
            lpn_manual = st.text_input("LPN")
            
            enviar = st.form_submit_button("Validar e Salvar")
            if enviar:
                # Salvar na planilha
                try:
                    aba_dados = gc_sheet.worksheet("Base_Dados")
                    aba_dados.append_row([
                        str(datetime.now()),
                        mat_manual,
                        lote_manual,
                        lpn_manual,
                        "Validado Manualmente"
                    ])
                    st.success("Salvo com sucesso na planilha!")
                except Exception as ex:
                    st.error(f"Erro ao salvar: {ex}")

# ABA 2: CONSULTAR PLANILHA
elif aba_selecionada == "Consultar Planilha":
    st.subheader("Registros Salvos")
    
    try:
        aba_dados = gc_sheet.worksheet("Base_Dados")
        dados_tabela = aba_dados.get_all_records()
        
        if dados_tabela:
            df = pd.DataFrame(dados_tabela)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("A planilha tá vazia por enquanto.")
            
    except Exception as e:
        st.error(f"Não consegui carregar os dados da aba: {e}")
