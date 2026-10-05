import streamlit as st

# Configuração basica da pagina
st.set_page_config(
    page_title="Painel de Validação de LPN", page_icon="📦", layout="wide"
)

# Estilo CSS para criar a fitinha verde diagonal no canto do card
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
        overflow: hidden; /* Corta o que passar da bordinha */
    }

    .ribbon-novo {
        position: absolute;
        top: 12px;
        right: -35px;
        transform: rotate(45deg);
        background-color: #28a745; /* Cor verde da fita */
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

# Guarda na sessao qual foi o ultimo pedido que gerou LPN
if "pedido_recente_id" not in st.session_state:
  st.session_state.pedido_recente_id = None

# Simulando a lista de pedidos que vem da planilha
pedidos_do_sistema = [
    {"id": "1058", "cliente": "Empresa A", "produto": "Item X - Qtd: 10"},
    {"id": "1057", "cliente": "Empresa B", "produto": "Item Y - Qtd: 5"},
    {"id": "1056", "cliente": "Empresa C", "produto": "Item Z - Qtd: 2"},
]

# Area lateral para testes
st.sidebar.header("Ações do Sistema")

pedido_selecionado = st.sidebar.selectbox(
    "Selecionar Pedido", [p["id"] for p in pedidos_do_sistema]
)

# Quando clica no botao, marca esse pedido como o "novo" da vez
if st.sidebar.button("Gerar/Solicitar LPN"):
  st.session_state.pedido_recente_id = pedido_selecionado
  st.rerun()

# Botao pra limpar o estado (simula o F5)
if st.sidebar.button("Limpar Status"):
  st.session_state.pedido_recente_id = None
  st.rerun()

st.divider()

# Mostrando os pedidos na tela
st.subheader("Lista de Pedidos")

for p in pedidos_do_sistema:
  # Verifica se esse pedido é o recém-solicitado
  is_novo = p["id"] == st.session_state.pedido_recente_id

  # Monta o card (se for novo, injeta a div da fita verde)
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
