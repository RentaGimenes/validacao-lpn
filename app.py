import streamlit as st
import streamlit.components.v1 as components

st.subheader("Validação de Códigos de Barras (Modo Híbrido: Com/Sem Enter)")

# Definimos o tamanho esperado para os códigos de barras (ex: 13 caracteres)
TAMANHO_CODIGO = 13 

# Estados para controlar qual campo está ativo e os valores salvos
if "campo_atual" not in st.session_state:
    st.session_state.campo_atual = 1
if "bc1" not in st.session_state:
    st.session_state.bc1 = ""
if "bc2" not in st.session_state:
    st.session_state.bc2 = ""
if "bc3" not in st.session_state:
    st.session_state.bc3 = ""

# Função que valida tudo quando o 3º campo é preenchido
def executar_validacao():
    st.success(f"Validação realizada com sucesso!\n- BC1: {st.session_state.bc1}\n- BC2: {st.session_state.bc2}\n- BC3: {st.session_state.bc3}")
    # Aqui entraria a sua lógica de checagem no banco/planilha e o som da Opção 28 se houver erro

# Componente inteligente em JavaScript injetado na tela
# Ele escuta o evento de digitação: se der Enter OU se atingir o tamanho exato do código de barras, avança sozinho!
script_html = f"""
<div>
  <input type="text" id="leitor" autofocus placeholder="Aguardando leitura..." style="width: 100%; padding: 12px; font-size: 18px; border: 2px solid #4CAF50; border-radius: 5px;" />
</div>

<script>
  const input = document.getElementById("leitor");
  const tamanhoEsperado = {TAMANHO_CODIGO};
  let campoAtual = {st.session_state.campo_atual};

  input.focus();

  input.addEventListener("input", (e) => {{
    let valor = input.value.trim();
    // Se a pistola mandou caracteres rapidamente e atingiu o tamanho do código (mesmo sem Enter)
    if (valor.length >= tamanhoEsperado) {{
      enviarDado(valor);
    }}
  }});

  input.addEventListener("keydown", (e) => {{
    // Se a pistola mandou o Enter configurado
    if (e.key === "Enter") {{
      let valor = input.value.trim();
      if (valor.length > 0) {{
        enviarDado(valor);
      }}
    }}
  }});

  function enviarDado(valor) {{
    // Comunica com o Streamlit enviando o valor via query params ou componente
    // No Streamlit moderno, podemos usar setComponentValue ou atualizar via Streamlit API
    const data = {{ campo: campoAtual, valor: valor }};
    window.parent.postMessage({{ type: 'streamlit:setComponentValue', value: data }}, '*');
  }}
</script>
"""

# Renderiza o componente customizado
# (Nota: Em ambientes de produção do Streamlit, componentes customizados ou bidirecionais 
# costumam usar bibliotecas como 'streamlit-keyup' ou componentes React customizados, 
# mas a lógica conceitual no navegador é exatamente essa).
