import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
from io import BytesIO
import cv2
import numpy as np

st.set_page_config(page_title="Captura Producción")

st.title("📋 Captura de Producción")

archivo = st.file_uploader(
    "Sube una foto",
    type=["jpg", "png", "jpeg"]
)

def ocr_zona(img, x1, y1, x2, y2):

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

    alto, ancho = img.shape[:2]

    datos = {

        "Fecha de elaboración":
            ocr_zona(img, 350, 180, 760, 240),

        "Maquinista":
            ocr_zona(img, 350, 240, 760, 310),

        "Máquina No.":
            ocr_zona(img, 350, 300, 760, 360),

        "Carretilla":
            ocr_zona(img, 350, 350, 760, 410),

        "Código de rollo":
            ocr_zona(img, 350, 400, 760, 470),

        "Tipo de bolsa":
            ocr_zona(img, 350, 460, 760, 520),

        "Tamaño":
            ocr_zona(img, 350, 520, 760, 580),

        "Enfajillador":
            ocr_zona(img, 350, 650, 760, 720),

        "Número de fajillas":
            ocr_zona(img, 350, 720, 760, 780),

        "Empacador":
            ocr_zona(img, 350, 850, 760, 920),

        "Número de bultos":
            ocr_zona(img, 350, 920, 760, 980),
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
            engine='openpyxl'
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
