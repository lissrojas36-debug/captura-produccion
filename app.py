import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO
import easyocr
import cv2
import numpy as np

st.set_page_config(page_title="Captura Producción")

st.title("📋 Captura automática")

archivo = st.file_uploader(
    "Sube una foto",
    type=["jpg", "jpeg", "png"]
)

reader = easyocr.Reader(['es'], gpu=False)

def leer_zona(img, x1, y1, x2, y2):

    zona = img[y1:y2, x1:x2]

    resultado = reader.readtext(zona)

    texto = " ".join([r[1] for r in resultado])

    return texto

if archivo:

    imagen = Image.open(archivo)

    img = np.array(imagen)

    st.image(imagen, use_container_width=True)

    datos = {

        "Fecha de elaboración":
            leer_zona(img, 400, 180, 900, 260),

        "Maquinista":
            leer_zona(img, 400, 240, 900, 340),

        "Máquina No.":
            leer_zona(img, 500, 320, 900, 400),

        "Carretilla":
            leer_zona(img, 500, 390, 900, 470),

        "Código de rollo":
            leer_zona(img, 400, 450, 900, 560),

        "Tipo de bolsa":
            leer_zona(img, 500, 540, 900, 620),

        "Tamaño":
            leer_zona(img, 500, 620, 900, 700),

        "Enfajillador":
            leer_zona(img, 400, 760, 900, 860),

        "Número de fajillas":
            leer_zona(img, 500, 860, 900, 940),

        "Empacador":
            leer_zona(img, 400, 1020, 900, 1120),

        "Número de bultos":
            leer_zona(img, 500, 1120, 900, 1200),
    }

    st.subheader("Datos capturados")

    df = pd.DataFrame([datos])

    st.dataframe(df)

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False
        )

    output.seek(0)

    st.download_button(
        "⬇ Descargar Excel",
        data=output,
        file_name="captura_produccion.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
