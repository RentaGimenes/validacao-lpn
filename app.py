import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Painel de Validação de LPN", page_icon="📦", layout="wide"
)

# --- CSS PERSONALIZADO (Estilo do Card e da Fitinha Diagonal) ---
st.markdown(
    """
    <style>
    .pedido-card {
        position: relative;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        overflow: hidden; /* Corta o excesso da fita para ficar certinha no canto */
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .ribbon-novo {
        position: absolute;
        top: 12px;
        right: -35px;
        transform: rotate(45deg);
        background-color: #28a745; /* Verde */
        color: white;
        text-align: center;
        font-size: 10px;
        font-weight: bold;
        padding: 4px 35px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        letter-spacing: 0.5px;
        text-transform: uppercase;
        z-index: 10;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📦 Painel de Pedidos e Validação de LPNs")

# --- INICIALIZAÇÃO DO SESSION STATE ---
# Controla qual pedido acabou de ter a LPN solicitada
if "pedido_recente_id" not in st.session_state:
  st.session_state.pedido_recente_id = None

# --- SIMULAÇÃO DE DADOS (Substitua pela leitura da sua planilha/Forms) ---
# Aqui você puxaria os dados reais da sua planilha integrada ao Forms
pedidos_do_sistema = [
    {"id": "1058", "cliente": "Empresa A", "produto": "Item X - Qtd: 10"},
    {"id": "1057", "cliente": "Empresa B", "produto": "Item Y - Qtd: 5"},
    {"id": "1056", "cliente": "Empresa C", "produto": "Item Z - Qtd: 2"},
]

# --- PAINEL LATERAL PARA AÇÕES ---
st.sidebar.header("Ações do Sistema")

# Seleção de qual pedido vai receber a solicitação de LPN para teste
pedido_selecionado = st.sidebar.selectbox(
    "Selecionar Pedido para Gerar LPN", [p["id"] for p in pedidos_do_sistema]
)

if st.sidebar.button("Gerar/Solicitar LPN"):
  # Define o pedido atual como o recém-solicitado
  st.session_state.pedido_recente_id = pedido_selecionado
  st.rerun()

if st.sidebar.button("Limpar Estado (Simular F5 / Recarregar)"):
  st.session_state.pedido_recente_id = None
  st.rerun()

st.sidebar.info(
    "Dica: Ao atualizar a página (F5) ou clicar no botão de limpar, a fitinha"
    " verde some."
)

st.divider()

# --- RENDERIZAÇÃO DOS PEDIDOS NA TELA ---
st.subheader("Lista de Pedidos")

for p in pedidos_do_sistema:
  # Verifica se este pedido específico é o que acabou de ter a LPN solicitada
  is_novo = p["id"] == st.session_state.pedido_recente_id

  # Montagem estruturada do card com ou sem a fita
  if is_novo:
    card_conteudo = f"""
        <div class="pedido-card">
            <div class="ribbon-novo">Novo</div>
            <h4 style="margin: 0 0 10px 0; color: #333;">Pedido #{p['id']}</h4>
            <p style="margin: 4px 0;"><b>Cliente:</b> {p['cliente']}</p>
            <p style="margin: 4px 0;"><b>Dados:</b> {p['produto']}</p>
        </div>
        """
  else:
    card_conteudo = f"""
        <div class="pedido-card">
            <h4 style="margin: 0 0 10px 0; color: #333;">Pedido #{p['id']}</h4>
            <p style="margin: 4px 0;"><b>Cliente:</b> {p['cliente']}</p>
            <p style="margin: 4px 0;"><b>Dados:</b> {p['produto']}</p>
        </div>
        """

  st.markdown(card_conteudo, unsafe_allow_html=True)
