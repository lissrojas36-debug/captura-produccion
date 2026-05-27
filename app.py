import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO
import easyocr
import numpy as np
import cv2
from streamlit_cropper import st_cropper

st.set_page_config(page_title="Captura Producción", layout="wide")

st.title("📋 Captura automática con recorte")

archivo = st.file_uploader("Sube una foto", type=["jpg", "jpeg", "png"])

reader = easyocr.Reader(["es"], gpu=False)

def leer_zona(img, x1, y1, x2, y2):
    zona = img[y1:y2, x1:x2]
    gris = cv2.cvtColor(zona, cv2.COLOR_RGB2GRAY)
    gris = cv2.resize(gris, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gris = cv2.GaussianBlur(gris, (3, 3), 0)

    thresh = cv2.threshold(
        gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    detect_horizontal = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2
    )

    cnts = cv2.findContours(
        detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )[0]

    for c in cnts:
        cv2.drawContours(thresh, [c], -1, (255, 255, 255), 2)

    resultado = reader.readtext(thresh, detail=0, paragraph=True)
    return " ".join(resultado).strip()

if archivo:
    imagen = Image.open(archivo).convert("RGB")

    st.subheader("1️⃣ Recorta solo el área del formato")
    box = st_cropper(
        imagen,
        realtime_update=True,
        box_color="#FF0000",
        aspect_ratio=None,
        return_type="box"
    )

    if box:
        x1 = int(box["left"])
        y1 = int(box["top"])
        x2 = int(box["left"] + box["width"])
        y2 = int(box["top"] + box["height"])

        recorte = imagen.crop((x1, y1, x2, y2))
        st.image(recorte, caption="Área recortada", use_container_width=True)

        if st.button("🔍 Escanear recorte"):
            img = np.array(recorte)

            datos = {
                "Fecha de elaboración": leer_zona(img, 400, 320, 837, 393),
                "Maquinista": leer_zona(img, 400, 371, 834, 430),
                "Máquina No.": leer_zona(img, 400, 429, 834, 481),
                "Carretilla": leer_zona(img, 400, 481, 834, 535),
                "Código de rollo": leer_zona(img, 395, 524, 900, 595),
                "Tipo de bolsa": leer_zona(img, 395, 578, 900, 636),
                "Tamaño": leer_zona(img, 395, 633, 900, 689),
                "Enfajillador": leer_zona(img, 395, 780, 900, 872),
                "Número de fajillas": leer_zona(img, 395, 870, 900, 926),
                "Empacador": leer_zona(img, 395, 1044, 900, 1100),
                "Número de bultos": leer_zona(img, 395, 1087, 900, 1151),
            }

            st.subheader("2️⃣ Datos detectados")

            for campo in datos:
                datos[campo] = st.text_input(campo, datos[campo])

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
