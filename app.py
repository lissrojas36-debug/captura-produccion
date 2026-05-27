import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import re
from io import BytesIO

st.set_page_config(page_title="Captura de Producción", layout="centered")

st.title("📋 Captura de Producción")
st.write("Sube una foto del formato para extraer los datos automáticamente.")

pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

archivo = st.file_uploader(
    "Sube una imagen",
    type=["jpg", "jpeg", "png"]
)

def limpiar(texto):
    return texto.replace("\n", " ").strip()

def buscar(patron, texto):
    resultado = re.search(patron, texto, re.IGNORECASE)
    if resultado:
        return resultado.group(1).strip()
    return ""

if archivo:

    imagen = Image.open(archivo)

    st.image(imagen, caption="Imagen subida", use_container_width=True)

    texto = pytesseract.image_to_string(imagen, lang="spa")

    texto = limpiar(texto)

    st.subheader("Texto detectado")
    st.text_area("", texto, height=250)

    datos = {
        "Fecha de elaboración":
            buscar(r"FECHA DE ELABORACION[:\s]*(.*?)(MAQUINISTA|MAQUINA)", texto),

        "Maquinista":
            buscar(r"MAQUINISTA[:\s]*(.*?)(MAQUINA)", texto),

        "Máquina No.":
            buscar(r"MAQUINA No\.?[:\s]*(.*?)(CARRETILLA)", texto),

        "Carretilla":
            buscar(r"CARRETILLA No\.?[:\s]*(.*?)(CODIGO)", texto),

        "Código de rollo":
            buscar(r"CODIGO ROLLO[:\s]*(.*?)(TIPO)", texto),

        "Tipo de bolsa":
            buscar(r"TIPO DE BOLSA[:\s]*(.*?)(TAMAÑO|TAMANO)", texto),

        "Tamaño":
            buscar(r"(?:TAMAÑO|TAMANO)[:\s]*(.*?)(MILLARES|FAJILLA)", texto),

        "Enfajillador":
            buscar(r"ENFAJILLADOR[:\s]*(.*?)(No\.? DE FAJILLAS)", texto),

        "Número de fajillas":
            buscar(r"No\.? DE FAJILLAS[:\s]*(.*?)(SOBRANTE)", texto),

        "Empacador":
            buscar(r"EMPACADOR[:\s]*(.*?)(No\.? DE BULTOS)", texto),

        "Número de bultos":
            buscar(r"No\.? DE BULTOS[:\s]*(.*)", texto),
    }

    st.subheader("Datos capturados")

    for campo in datos:
        datos[campo] = st.text_input(campo, datos[campo])

    if st.button("📥 Generar Excel"):

        df = pd.DataFrame([datos])

        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Produccion')

        output.seek(0)

        st.download_button(
            label="⬇ Descargar Excel",
            data=output,
            file_name="captura_produccion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
