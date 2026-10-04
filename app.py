import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Validação de LPN", layout="centered")

st.title("📦 Validação de LPNs em Sequência")
st.write("Bipe os códigos em sequência. O foco mudará automaticamente para o próximo campo ao pressionar Enter sem recarregar a página.")

# Número de campos LPN que você deseja na tela (ajuste conforme sua necessidade)
TOTAL_CAMPOS = 5

# Criando um formulário ou container para os inputs
st.markdown("### Digite ou Bipe os Códigos:")

lpns_capturadas = []

# Criamos os inputs de texto na tela
for i in range(1, TOTAL_CAMPOS + 1):
    # Usamos o session_state para persistir os valores se houver alguma interação externa
    val = st.text_input(f"LPN {i:02d}", key=f"lpn_{i}")
    lpns_capturadas.append(val)

# Script JavaScript para interceptar a tecla Enter e mover o foco entre os inputs do Streamlit
js_code = """
<script>
function setupBarcodeNavigation() {
    const doc = window.parent.document;
    const inputs = doc.querySelectorAll('input[type="text"]');
    
    inputs.forEach((input, index) => {
        // Evita múltiplos listeners duplicados
        if (input.dataset.listenerAttached) return;
        input.dataset.listenerAttached = "true";
        
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const allInputs = Array.from(doc.querySelectorAll('input[type="text"]'));
                const currentIndex = allInputs.indexOf(e.target);
                
                if (currentIndex !== -1 && currentIndex + 1 < allInputs.length) {
                    allInputs[currentIndex + 1].focus();
                    allInputs[currentIndex + 1].select();
                }
            }
        });
    });
}

// Executa logo após carregar e observa mudanças no DOM caso o Streamlit re-renderize partes da página
setupBarcodeNavigation();
const observer = new MutationObserver(setupBarcodeNavigation);
observer.observe(window.parent.document.body, { childList: true, subtree: true });
</script>
"""

# Injeta o script na aplicação
components.html(js_code, height=0, width=0)

st.markdown("---")

# Botão para processar os dados coletados de uma só vez
if st.button("Validar / Processar LPNs", type="primary"):
    # Filtra apenas os campos que foram preenchidos
    preenchidos = [lpn for lpn in lpns_capturadas if lpn.strip() != ""]
    
    if not preenchidos:
        st.warning("Nenhuma LPN foi bipada ou preenchida.")
    else:
        st.success(f"Total de {len(preenchidos)} LPN(s) capturadas com sucesso!")
        st.write("Valores lidos:", preenchidos)
        
        # Aqui você pode colocar a sua lógica de validação no banco de dados, planilha, etc.
