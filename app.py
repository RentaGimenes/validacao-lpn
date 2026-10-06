from datetime import datetime, time, timedelta
import gspread
import pandas as pd
import pytz
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Validação LPN - Rigor", page_icon="📦", layout="wide"
)

# Definição do fuso horário de Brasília para garantir o reset correto à meia-noite
TZ_BRASILIA = pytz.timezone("America/Sao_Paulo")


def formatar_lote_lido_rigor(codigo):
  """Função para tratar e formatar o código lido conforme o rigor do processo."""
  if not codigo:
    return ""
  return str(codigo).strip().upper()


# Função para conectar ao Google Sheets (ajuste conforme suas credenciais/secrets)
@st.cache_resource
def conectar_google_sheets():
  scope = [
      "https://spreadsheets.google.com/feeds",
      "https://www.googleapis.com/auth/drive",
  ]
  # Se utilizar st.secrets para credenciais:
  try:
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client
  except Exception as e:
    st.error(
        f"Erro ao conectar com as credenciais do Google Sheets: {e}"
    )
    return None


def main():
  st.title("📦 Sistema de Validação LPN - Rigor")
  st.sidebar.header("Painel de Controle")

  # Inicialização do estado da sessão para controle dos pedidos
  if "pedidos_concluidos" not in st.session_state:
    st.session_state.pedidos_concluidos = []

  # Hora atual em Brasília
  agora_brasilia = datetime.now(TZ_BRASILIA)

  # Lógica de controle de limpeza diária à meia-noite (filtra apenas o dia atual)
  # Remove itens concluídos em datas anteriores para garantir o comportamento de reset à meia-noite
  if "ultima_verificacao_data" not in st.session_state:
    st.session_state.ultima_verificacao_data = agora_brasilia.date()
  elif st.session_state.ultima_verificacao_data != agora_brasilia.date():
    # Mudança de dia: limpa os concluídos do dia anterior
    st.session_state.pedidos_concluidos = []
    st.session_state.ultima_verificacao_data = agora_brasilia.date()

  # Abas da Aplicação
  aba1, aba2 = st.tabs(
      ["🔍 Validação e Leitura", "📋 Histórico de Concluídos (Hoje)"]
  )

  with aba1:
    st.subheader("Leitura de Etiquetas LPN")

    codigo_input = st.text_input(
        "Escaneie ou digite o código do lote/LPN:", key="input_lpn"
    )

    if st.button("Validar", type="primary"):
      codigo_formatado = formatar_lote_lido_rigor(codigo_input)

      if not codigo_formatado:
        st.warning("Por favor, insira um código válido.")
      else:
        # Registro do sucesso e adição aos concluídos com timestamp atual
        horario_registro = agora_brasilia.strftime("%H:%M:%S")

        # Evita duplicatas imediatas se necessário, ou apenas registra
        novo_registro = {
            "Codigo": codigo_formatado,
            "Horario": horario_registro,
            "Data": agora_brasilia.date(),
        }

        st.session_state.pedidos_concluidos.append(novo_registro)
        st.success(
            f"✅ Código **{codigo_formatado}** validado e registrado com sucesso"
            f" às {horario_registro}!"
        )

  with aba2:
    st.subheader("Pedidos Concluídos no Dia Atual")
    if st.session_state.pedidos_concluidos:
      df_concluidos = pd.DataFrame(st.session_state.pedidos_concluidos)
      st.dataframe(df_concluidos[["Codigo", "Horario"]], use_container_width=True)
      st.info(
          "ℹ️ Os registros são mantidos durante o dia e reiniciados"
          " automaticamente à meia-noite."
      )
    else:
      st.info("Nenhum pedido concluído registrado hoje até o momento.")


if __name__ == "__main__":
  main()
