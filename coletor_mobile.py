import pandas as pd
import requests
import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner

st.set_page_config(page_title="Coletor Mobile + API", layout="centered")
st.title("Coletor de Materiais")

if "itens_coletados" not in st.session_state:
  st.session_state.itens_coletados = []
if "codigo_atual" not in st.session_state:
  st.session_state.codigo_atual = None
if "dados_api" not in st.session_state:
  st.session_state.dados_api = {}


@st.cache_data(ttl=3600)
def buscar_dados_mestres(ean):
  url = f"https://openfoodfacts.org{ean}.json"
  try:
    resposta = requests.get(url, timeout=5)
    if resposta.status_code == 200:
      dados = resposta.json()
      if dados.get("status") == 1:
        produto = dados.get("product", {})
        nome = (
            produto.get("product_name_pt")
            or produto.get("product_name")
            or "Produto sem descrição"
        )
        marca = produto.get("brands", "Não informada")
        embalagem = produto.get("quantity", "UN")
        return {
            "encontrado": True,
            "descricao": nome,
            "marca": marca,
            "embalagem": embalagem,
        }
  except Exception:
    pass
  return {
      "encontrado": False,
      "descricao": "",
      "marca": "",
      "embalagem": "UN",
  }


codigo_lido = qrcode_scanner(key="scanner_ao_vivo")

if codigo_lido and codigo_lido != st.session_state.codigo_atual:
  st.session_state.codigo_atual = codigo_lido
  with st.spinner("Buscando dados mestres na API..."):
    st.session_state.dados_api = buscar_dados_mestres(codigo_lido)

if st.session_state.codigo_atual:
  st.info(f"**Código bipado:** {st.session_state.codigo_atual}")

  info = st.session_state.dados_api
  if info.get("encontrado"):
    st.success("Material localizado na base pública!")
  else:
    st.warning("Material não encontrado na API. Preencha os dados manualmente.")

  with st.form("form_quantidade", clear_on_submit=True):
    descricao = st.text_input(
        "Descrição do Material", value=info.get("descricao", "")
    )
    marca = st.text_input("Marca / Fabricante", value=info.get("marca", ""))
    unidade = st.text_input(
        "Unidade / Embalagem", value=info.get("embalagem", "UN")
    )
    quantidade = st.number_input(
        "Quantidade", min_value=0.01, value=1.0, step=1.0
    )

    col1, col2 = st.columns(2)
    confirmar = col1.form_submit_button("Salvar Item", use_container_width=True)
    cancelar = col2.form_submit_button("Cancelar", use_container_width=True)

    if confirmar:
      st.session_state.itens_coletados.append({
          "Código (EAN)": st.session_state.codigo_atual,
          "Descrição": descricao if descricao else "Sem descrição",
          "Marca": marca,
          "Unidade": unidade,
          "Quantidade": quantidade,
      })
      st.session_state.codigo_atual = None
      st.rerun()

    if cancelar:
      st.session_state.codigo_atual = None
      st.rerun()

if st.session_state.itens_coletados:
  st.divider()
  st.subheader(f"Resumo da Coleta ({len(st.session_state.itens_coletados)} itens)")
  df = pd.DataFrame(st.session_state.itens_coletados)
  st.dataframe(df, use_container_width=True)

  csv = df.to_csv(index=False, sep=";").encode("utf-8-sig")
  st.download_button(
      label="Baixar Planilha (CSV para Excel)",
      data=csv,
      file_name="inventario_coletado.csv",
      mime="text/csv",
      use_container_width=True,
  )
