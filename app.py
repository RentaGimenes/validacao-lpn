import streamlit as st

# Configuração básica da página do Streamlit
st.set_page_config(page_title="Validação de LPNs", layout="wide")

# Exemplo de variável contendo a tag HTML do GIF (substitua pelo seu código real do GIF se necessário)
sonic_html = '<img src="seu_gif_aqui.gif" width="80px">'

# Título principal da aplicação
st.title("Sistema de Verificação e Comparação de LPNs")

# Início da seção do retângulo de aviso com fundo preto
st.markdown(
    f"""
    <div style="background-color: #000000; border: 2px solid #f1c40f; padding: 16px; border-radius: 8px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between;">
        
        <!-- Bloco de texto de aviso em destaque -->
        <div style="color: #f1c40f; font-size: 15px; font-weight: bold; line-height: 1.5; flex-grow: 1;">
            ⚠️ LPNs MERAMENTE ILUSTRATIVAS<br>
            SEUS VALORES DEVEM SER CONSIDERADOS APENAS COMO EXEMPLO PARA FACILITAR A VISUALIZAÇÃO DA DIVERGÊNCIA.
        </div>
        
        <!-- Bloco contendo o GIF com fundo integrado ao preto -->
        <div style="width: 100px; height: 80px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; padding-left: 15px;">
            {sonic_html}
        </div>
        
    </div>
    """,
    unsafe_allow_html=True,
)

# Espaço para o restante da sua lógica e código do app
st.write("---")
st.write("Aqui continua o restante da interface do seu aplicativo Python com Streamlit.")
