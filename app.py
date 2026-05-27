import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
from io import BytesIO
import easyocr
import numpy as np
import cv2
from streamlit_cropper import st_cropper

st.set_page_config(page_title="Captura Producción", layout="wide")

st.title("📋 Captura automática con zonas de colores")

archivo = st.file_uploader("Sube una foto del formato", type=["jpg", "jpeg", "png"])

@st.cache_resource
def cargar_ocr():
    return easyocr.Reader(["es"], gpu=False)

reader = cargar_ocr()

BASE_W = 900
BASE_H = 1151

ZONAS = {
    "Fecha de elaboración": {"coords": (400, 320, 837, 393), "color": "red"},
    "Maquinista": {"coords": (400, 371, 834, 430), "color": "blue"},
    "Máquina No.": {"coords": (400, 429, 834, 481), "color": "green"},
    "Carretilla": {"coords": (400, 481, 834, 535), "color": "orange"},
    "Código de rollo": {"coords": (395, 524, 900, 595), "color": "purple"},
    "Tipo de bolsa": {"coords": (395, 578, 900, 636), "color": "brown"},
    "Tamaño": {"coords": (395, 633, 900, 689), "color": "cyan"},
    "Enfajillador": {"coords": (395, 780, 900, 872), "color": "magenta"},
    "Número de fajillas": {"coords": (395, 870, 900, 926), "color": "lime"},
    "Empacador": {"coords": (395, 1044, 900, 1100), "color": "navy"},
    "Número de bultos": {"coords": (395, 1087, 900, 1151), "color": "black"},
}

def escalar_coords(coords, ancho, alto):
    x1, y1, x2, y2 = coords
    return (
        int(x1 * ancho / BASE_W),
        int(y1 * alto / BASE_H),
        int(x2 * ancho / BASE_W),
        int(y2 * alto / BASE_H),
    )

def limpiar_ocr(texto):
    return (
        texto.replace("|", "1")
        .replace("—", "-")
        .replace("_", "")
        .replace("  ", " ")
        .strip()
    )

def leer_zona(img, x1, y1, x2, y2):
    zona = img[y1:y2, x1:x2]

    if zona.size == 0:
        return ""

    gris = cv2.cvtColor(zona, cv2.COLOR_RGB2GRAY)
    gris = cv2.resize(gris, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gris = cv2.GaussianBlur(gris, (3, 3), 0)

    thresh = cv2.threshold(
        gris,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (45, 1))
    detect_horizontal = cv2.morphologyEx(
        thresh,
        cv2.MORPH_OPEN,
        horizontal_kernel,
        iterations=2
    )

    cnts = cv2.findContours(
        detect_horizontal,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )[0]

    for c in cnts:
        cv2.drawContours(thresh, [c], -1, (255, 255, 255), 3)

    resultado = reader.readtext(thresh, detail=0, paragraph=True)

    return limpiar_ocr(" ".join(resultado))

def dibujar_zonas(imagen):
    copia = imagen.copy()
    draw = ImageDraw.Draw(copia)
    ancho, alto = copia.size

    for campo, info in ZONAS.items():
        x1, y1, x2, y2 = escalar_coords(info["coords"], ancho, alto)
        color = info["color"]

        draw.rectangle((x1, y1, x2, y2), outline=color, width=4)
        draw.text((x1, max(0, y1 - 18)), campo, fill=color)

    return copia

if archivo:
    imagen_original = Image.open(archivo).convert("RGB")

    st.subheader("1️⃣ Recorta solo la hoja")
    box = st_cropper(
        imagen_original,
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

        recorte = imagen_original.crop((x1, y1, x2, y2))

        st.subheader("2️⃣ Zonas detectadas por color")
        imagen_zonas = dibujar_zonas(recorte)
        st.image(imagen_zonas, use_container_width=True)

        if st.button("🔍 Escanear zonas"):
            img = np.array(recorte)
            ancho, alto = recorte.size

            datos = {}

            for campo, info in ZONAS.items():
                zx1, zy1, zx2, zy2 = escalar_coords(info["coords"], ancho, alto)
                datos[campo] = leer_zona(img, zx1, zy1, zx2, zy2)

            st.subheader("3️⃣ Datos detectados")

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
