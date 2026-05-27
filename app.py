import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
from io import BytesIO
import cv2
import numpy as np

st.set_page_config(page_title="Captura Producción")

st.title("📋 Captura Producción")

archivo = st.file_uploader(
    "Sube una foto",
    type=["jpg", "jpeg", "png"]
)

def leer_zona(img, x1, y1, x2, y2):

    zona = img[y1:y2, x1:x2]

    gris = cv2.cvtColor(zona, cv2.COLOR_BGR2GRAY)

    gris = cv2.GaussianBlur(gris, (3,3), 0)

    thresh = cv2.threshold(
        gris,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    texto = pytesseract.image_to_string(
        thresh,
        config='--psm 7'
    )

    return texto.strip()

if archivo:

    imagen = Image.open(archivo)

    img = np.array(imagen)

    st.image(imagen, use_container_width=True)

    datos = {

        "Fecha de elaboración":
            leer_zona(img, 420, 180, 860, 250),

        "Maquinista":
            leer_zona(img, 420, 240, 860, 330),

        "Máquina No.":
            leer_zona(img, 520, 330, 860, 390),

        "Carretilla":
            leer_zona(img, 520, 390, 860, 450),

        "Código de rollo":
            leer_zona(img, 420, 450, 860, 550),

        "Tipo de bolsa":
            leer_zona(img, 520, 540, 860, 620),

        "Tamaño":
            leer_zona(img, 520, 610, 860, 690),

        "Enfajillador":
            leer_zona(img, 420, 760, 860, 860),

        "Número de fajillas":
            leer_zona(img, 520, 850, 860, 930),

        "Empacador":
            leer_zona(img, 420, 1030, 860, 1130),

        "Número de bultos":
            leer_zona(img, 520, 1130, 860, 1210),
    }

    st.subheader("Datos capturados")

    for campo in datos:
        datos[campo] = st.text_input(
            campo,
            datos[campo]
        )

    if st.button("📥 Generar Excel"):

        df = pd.DataFrame([datos])

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
