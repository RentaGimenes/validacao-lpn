import streamlit as st

# Título da aplicação
st.title("Validação de LPN / Códigos de Barras")

# Formulário para garantir que o Enter em qualquer campo submeta os dados de forma limpa
with st.form(key="form_validacao"):
    bc1 = st.text_input("1º Código de Barras")
    bc2 = st.text_input("2º Código de Barras")
    bc3 = st.text_input("3º Código de Barras")

    # Botão de validação (que também é disparado ao dar Enter no último campo)
    submitted = st.form_submit_button("Validar Códigos")

if submitted:
    if bc1 and bc2 and bc3:
        # Aqui entra a sua lógica de validação (se der erro, toca o som da Opção 28)
        st.success(f"✅ Códigos validados com sucesso!\n- {bc1}\n- {bc2}\n- {bc3}")
    else:
        st.warning("⚠️ Por favor, preencha ou bipa todos os três códigos antes de validar.")
