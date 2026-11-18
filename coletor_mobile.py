import pandas as pd
import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner

st.set_page_config(page_title="Coletor Mobile", layout="centered")
st.title("Coletor de Códigos ao Vivo")

if "lista_codigos" not in st.session_state:
  st.session_state.lista_codigos = []

codigo = qrcode_scanner(key="scanner_ao_vivo")

if codigo:
  if not st.session_state.lista_codigos or st.session_state.lista_codigos[-1] != codigo:
    st.session_state.lista_codigos.append(codigo)
    st.success(f"Lido com sucesso: {codigo}")

if st.session_state.lista_codigos:
  st.subheader(f"Itens coletados ({len(st.session_state.lista_codigos)})")
  df = pd.DataFrame(st.session_state.lista_codigos, columns=["Código"])
  st.dataframe(df, use_container_width=True)

  csv = df.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="Baixar lista em CSV",
      data=csv,
      file_name="coleta_codigos.csv",
      mime="text/csv",
  )
