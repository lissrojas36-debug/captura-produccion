import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO
import easyocr
import numpy as np

st.set_page_config(page_title="Captura Producción", layout="wide")

st.title("📋 Captura automática de producción")

archivo = st.file_uploader("Sube una foto", type=["jpg", "jpeg", "png"])

reader = easyocr.Reader(["es"], gpu=False)

def leer_zona(img, x1, y1, x2, y2):
    zona = img[y1:y2, x1:x2]
    resultado = reader.readtext(zona)
    texto = " ".join([r[1] for r in resultado])
    return texto.strip()

if archivo:
    imagen = Image.open(archivo).convert("RGB")
    img = np.array(imagen)

    st.image(imagen, caption="Formato cargado", use_container_width=True)

    datos = {
        "Fecha de elaboración": leer_zona(img, 395, 320, 837, 393),
        "Maquinista": leer_zona(img, 395, 371, 834, 430),
        "Máquina No.": leer_zona(img, 395, 429, 834, 481),
        "Carretilla": leer_zona(img, 395, 481, 834, 535),
        "Código de rollo": leer_zona(img, 395, 524, 900, 595),
        "Tipo de bolsa": leer_zona(img, 395, 578, 900, 636),
        "Tamaño": leer_zona(img, 395, 633, 900, 689),
        "Enfajillador": leer_zona(img, 395, 780, 900, 872),
        "Número de fajillas": leer_zona(img, 395, 870, 900, 926),
        "Empacador": leer_zona(img, 395, 1044, 900, 1100),
        "Número de bultos": leer_zona(img, 395, 1087, 900, 1151),
    }

    st.subheader("Datos detectados")

    df = pd.DataFrame([datos])
    st.dataframe(df, use_container_width=True)

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
