import pandas as pd
from PIL import Image
from pyzbar.pyzbar import decode
import streamlit as st

st.set_page_config(page_title="Coletor de Estoque Mobile", layout="centered")

# Inicializa a lista de produtos monitoráveis na sessão
if "monitoraveis" not in st.session_state:
    st.session_state.monitoraveis = []

st.title("📱 Cadastro Rápido (Câmera)")
st.caption("Aponte a câmera para o código de barras do produto na prateleira.")

# --- 1. CAPTURA VIA CÂMERA DO CELULAR ---
foto = st.file_uploader("Toque para abrir a câmera do celular", type=["jpg", "jpeg", "png"])

codigo_lido = ""
if foto is not None:
    imagem = Image.open(foto)
    codigos = decode(imagem)
    if codigos:
        codigo_lido = codigos[0].data.decode("utf-8")
        st.success(f"Código lido: **{codigo_lido}**")
    else:
        st.warning(
            "Não foi possível ler o código na foto. Tente aproximar mais ou digitar abaixo."
        )

# --- 2. FORMULÁRIO DE CADASTRO DO ITEM MONITORÁVEL ---
with st.form("form_cadastro", clear_on_submit=True):
    ean = st.text_input(
        "Código de Barras (EAN)",
        value=codigo_lido,
        placeholder="Escaneie acima ou digite",
    )
    nome = st.text_input(
        "Nome do Produto (Opcional se já houver XML)",
        placeholder="Ex: Leite Integral 1L",
    )
    qtd_inicial = st.number_input(
        "Quantidade Atual na Prateleira / Estoque",
        min_value=0.0,
        step=1.0,
        format="%.0f",
    )
    monitorar = st.checkbox("Marcar como Produto Monitorável", value=True)

    salvar = st.form_submit_button(
        "✅ Salvar Produto Monitorável", use_container_width=True
    )

    if salvar:
        if not ean:
            st.error("Informe ou escaneie o código de barras.")
        else:
            # Atualiza se o EAN já estiver na lista, ou adiciona novo
            existente = next(
                (
                    item
                    for item in st.session_state.monitoraveis
                    if item["codigo"] == ean
                ),
                None,
            )
            if existente:
                existente["produto"] = nome if nome else existente["produto"]
                existente["estoque_inicial"] = qtd_inicial
                existente["monitoravel"] = monitorar
            else:
                st.session_state.monitoraveis.append({
                    "codigo": str(ean).strip(),
                    "produto": (
                        nome.strip().upper()
                        if nome
                        else f"PRODUTO EAN {ean}"
                    ),
                    "estoque_inicial": qtd_inicial,
                    "monitoravel": monitorar,
                })
            st.toast(f"Item {ean} salvo com sucesso!")

# --- 3. LISTA DOS 15-20 ITENS BIPADOS NA DEMONSTRAÇÃO ---
st.divider()
total_itens = len(st.session_state.monitoraveis)
st.subheader(f"📋 Itens Monitoráveis Cadastrados ({total_itens}/20)")

if total_itens > 0:
    df_monit = pd.DataFrame(st.session_state.monitoraveis)
    st.dataframe(df_monit, use_container_width=True, hide_index=True)

    # Botão para baixar o CSV pronto para alimentar o painel principal
    csv_pronto = df_monit.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Baixar Base de Monitoráveis (CSV)",
        data=csv_pronto,
        file_name="estoque_monitoraveis.csv",
        mime="text/csv",
        use_container_width=True,
    )
else:
    st.info("Nenhum produto bipado ainda. Use a câmera acima para começar.")
