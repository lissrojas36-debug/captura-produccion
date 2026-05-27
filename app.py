import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Captura Producción", layout="wide")

st.title("📋 Captura manual de producción")

if "registros" not in st.session_state:
    st.session_state.registros = []

archivo = st.file_uploader("Sube la foto del formato", type=["jpg", "jpeg", "png"])

col1, col2 = st.columns(2)

with col1:
    if archivo:
        imagen = Image.open(archivo)
        st.image(imagen, caption="Formato", use_container_width=True)

with col2:
    st.subheader("Captura de datos")

    fecha = st.text_input("Fecha de elaboración")
    maquinista = st.text_input("Maquinista")
    maquina = st.text_input("Máquina No.")
    carretilla = st.text_input("Carretilla")
    codigo = st.text_input("Código de rollo")
    tipo = st.text_input("Tipo de bolsa")
    tamano = st.text_input("Tamaño")
    enfajillador = st.text_input("Enfajillador")
    fajillas = st.text_input("Número de fajillas")
    empacador = st.text_input("Empacador")
    bultos = st.text_input("Número de bultos")

    if st.button("➕ Agregar registro"):
        st.session_state.registros.append({
            "Fecha de elaboración": fecha,
            "Maquinista": maquinista,
            "Máquina No.": maquina,
            "Carretilla": carretilla,
            "Código de rollo": codigo,
            "Tipo de bolsa": tipo,
            "Tamaño": tamano,
            "Enfajillador": enfajillador,
            "Número de fajillas": fajillas,
            "Empacador": empacador,
            "Número de bultos": bultos,
        })

        st.success("Registro agregado")

st.subheader("Registros capturados")

df = pd.DataFrame(st.session_state.registros)

st.dataframe(df, use_container_width=True)

if len(df) > 0:
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Produccion")

    output.seek(0)

    st.download_button(
        "⬇ Descargar Excel",
        data=output,
        file_name="captura_produccion.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
