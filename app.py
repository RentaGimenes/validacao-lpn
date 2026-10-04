import streamlit as st
import streamlit.components.v1 as components

# Inicializa o estado
for campo in ["bc1", "bc2", "bc3"]:
    if campo not in st.session_state:
        st.session_state[campo] = ""

st.title("Validação de LPN / Códigos de Barras")

# Campos nativos do Streamlit
st.text_input("1º Código de Barras", key="bc1")
st.text_input("2º Código de Barras", key="bc2")
st.text_input("3º Código de Barras", key="bc3")

if st.session_state.bc1 and st.session_state.bc2 and st.session_state.bc3:
    st.success("✅ Todos os códigos preenchidos! Executando validação...")

# Script em JavaScript para injetar o foco automático nos inputs do Streamlit
components.html(
    """
<script>
    const doc = window.parent.document;
    
    function configurarFoco() {
        const inputs = doc.querySelectorAll('input[type="text"]');
        if (inputs.length >= 3) {
            inputs[0].addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    setTimeout(() => inputs[1].focus(), 100);
                }
            });
            inputs[1].addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    setTimeout(() => inputs[2].focus(), 100);
                }
            });
        }
    }
    
    // Tenta configurar logo após carregar
    setTimeout(configurarFoco, 500);
</script>
""",
    height=0,
)
