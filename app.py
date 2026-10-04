import streamlit as st
import tkinter as tk
from tkinter import messagebox

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA DO STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Sistema de Verificação de LPNs",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. INICIALIZAÇÃO DE VARIÁVEIS DE ESTADO
# ==========================================
# Garante que os dados da sessão sejam mantidos entre as interações
if "lpn_atual" not in st.session_state:
    st.session_state.lpn_atual = ""
if "codigos_lidos" not in st.session_state:
    st.session_state.codigos_lidos = []

# Função para limpar os códigos e preparar para a próxima LPN
def limpar_para_proxima_lpn():
    st.session_state.codigos_lidos = []
    st.session_state.lpn_atual = ""

# ==========================================
# 3. COMPONENTES VISUAIS (ESTILO E AVISOS)
# ==========================================
# Exemplo de variável contendo a tag HTML do GIF (com fundo integrado ao preto)
sonic_html = '<img src="seu_gif_aqui.gif" width="80px">'

# Título principal da aplicação
st.title("📦 Sistema de Verificação e Comparação de LPNs")
st.write("Utilize este painel para realizar a leitura de etiquetas e conferência de divergências.")

# Retângulo de aviso com fundo totalmente preto (#000000) e borda amarela
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

# ==========================================
# 4. ENTRADA DE DADOS E LEITURA DE CÓDIGOS
# ==========================================
st.subheader("Entrada de Dados por Leitor / Código de Barras")

col1, col2 = st.columns([2, 1])

with col1:
    # Campo para capturar o código de barras ou LPN
    entrada_codigo = st.text_input("Bipe ou digite o código da etiqueta:", key="input_codigo")

with col2:
    st.write("")
    st.write("")
    # Botão para limpar os dados para a próxima LPN
    if st.button("Limpar para Próxima LPN", type="secondary"):
        limpar_para_proxima_lpn()
        st.rerun()

# Lógica para processar o código inserido
if entrada_codigo:
    # Adiciona o código lido à lista se ele ainda não estiver presente na sessão atual
    if entrada_codigo not in st.session_state.codigos_lidos:
        st.session_state.codigos_lidos.append(entrada_codigo)
        st.success(f"Código registrado com sucesso: {entrada_codigo}")
    else:
        st.warning("Este código já foi scaneado nesta LPN.")

# ==========================================
# 5. EXIBIÇÃO DE REGISTROS E COMPARAÇÃO
# ==========================================
st.markdown("---")
st.subheader("📋 Resumo dos Códigos Lidos para a LPN Atual")

if st.session_state.codigos_lidos:
    # Mostra os itens capturados em formato de tabela ou lista
    for i, codigo in enumerate(st.session_state.codigos_lidos, 1):
        st.text({i} - Código: {codigo})
else:
    st.info("Nenhum código lido no momento. Bipe uma etiqueta para começar.")

# ==========================================
# 6. INTEGRAÇÃO OPCIONAL COM TKINTER (CASO NECESSÁRIO)
# ==========================================
# Nota: Se você estiver rodando uma interface desktop local com Tkinter em paralelo,
# esta função pode ser chamada para disparar alertas nativos do sistema operacional.
def disparar_alerta_tkinter(mensagem):
    root = tk.Tk()
    root.withdraw() # Oculta a janela principal do Tkinter
    messagebox.showinfo("Aviso do Sistema", mensagem)
    root.destroy()
